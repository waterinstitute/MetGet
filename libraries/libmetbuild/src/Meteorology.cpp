// MIT License
//
// Copyright (c) 2020 ADCIRC Development Group
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// Author: Zach Cobell
// Contact: zcobell@thewaterinstitute.org
//
#include "Meteorology.h"

#include <cmath>
#include <fstream>
#include <iostream>
#include <utility>

#include "Logging.h"
#include "MetBuild_Status.h"
#include "Projection.h"
#include "Triangulation.h"
#include "data_sources/CoampsData.h"
#include "data_sources/GefsData.h"
#include "data_sources/GfsData.h"
#include "data_sources/Grib.h"
#include "data_sources/HrrrConusData.h"
#include "data_sources/HwrfData.h"
#include "data_sources/NamData.h"

using namespace MetBuild;

Meteorology::Meteorology(const MetBuild::Grid *windGrid,
                         Meteorology::SOURCE source,
                         MetBuild::GriddedDataTypes::TYPE type, bool backfill,
                         int epsg_output)
    : m_type(type),
      m_source(source),
      m_windGrid(windGrid),
      m_grid_positions(m_windGrid->grid_positions()),
      m_gridded1(nullptr),
      m_gridded2(nullptr),
      m_rate_scaling_1(1.0),
      m_rate_scaling_2(1.0),
      m_interpolation_1(nullptr),
      m_interpolation_2(nullptr),
      m_useBackgroundFlag(backfill),
      m_epsg_output(epsg_output),
      m_variables(generate_variable_list(type)) {
  // We assume that all data in the database is in WGS84 and the user can
  // get out other projections if they need to
  if (m_epsg_output != 4326) {
    m_grid_positions = Meteorology::reproject_grid(m_grid_positions);
  }
}

MetBuild::Grid::grid Meteorology::reproject_grid(MetBuild::Grid::grid g) const {
  std::vector<Point> pts;
  pts.reserve(g.size() * g[0].size());
  for (const auto &row : g) {
    for (const auto &v : row) {
      pts.push_back(v);
    }
  }
  bool latlon = true;
  auto pts_out = Projection::transform(m_epsg_output, 4326, pts, latlon);
  size_t count = 0;
  for (auto &row : g) {
    for (auto &v : row) {
      v = pts_out[count];
      count++;
    }
  }
  return g;
}

void Meteorology::set_next_file(const std::string &filename) {
  m_file1 = std::move(m_file2);
  m_file2 = {filename};
}

void Meteorology::set_next_file(const std::vector<std::string> &filenames) {
  m_file1 = std::move(m_file2);
  m_file2 = filenames;
}

int Meteorology::process_data() {
  assert(!m_file1.empty());
  assert(!m_file2.empty());

  if (m_file1.empty() || m_file2.empty()) {
    metbuild_throw_exception(
        "Files not specified before attempting to process.");
    return MB_ERROR;
  }

  if (m_gridded1 && m_gridded2) {
    if (m_file1 == m_gridded1->filenames() &&
        m_file2 == m_gridded2->filenames()) {
      return MB_NOERROR;
    }
  }

  if (m_gridded2) {
    if (m_gridded2->filenames() == m_file1) {
      m_gridded1.reset(nullptr);
      m_gridded1 = std::move(m_gridded2);
      m_interpolation_1 = std::move(m_interpolation_2);
    } else {
      m_gridded1 =
          MetBuild::Meteorology::gridded_data_factory(m_file1, m_source);
      m_interpolation_1 = std::make_shared<InterpolationData>(
          m_gridded1->generate_triangulation(), m_grid_positions);
    }
  } else {
    m_gridded1 = MetBuild::Meteorology::gridded_data_factory(m_file1, m_source);
    m_interpolation_1 = std::make_shared<InterpolationData>(
        m_gridded1->generate_triangulation(), m_grid_positions);
  }

  m_gridded2 = MetBuild::Meteorology::gridded_data_factory(m_file2, m_source);
  if (m_gridded1->latitude1d() == m_gridded2->latitude1d() &&
      m_gridded1->longitude1d() == m_gridded2->longitude1d()) {
    m_interpolation_2 = std::make_shared<InterpolationData>(*m_interpolation_1);
  } else {
    m_interpolation_2 = std::make_shared<InterpolationData>(
        m_gridded2->generate_triangulation(), m_grid_positions);
  }

  return MB_NOERROR;
}

MetBuild::MeteorologicalData<1> Meteorology::scalar_value_interpolation(
    const double time_weight) {
  MeteorologicalData<1> r(m_windGrid->ni(), m_windGrid->nj());

  if (time_weight < 0.0) {
    if (this->m_useBackgroundFlag) {
      r.fill(MeteorologicalData<1>::flag_value());
    } else {
      r.fill(0.0);
    }
    return r;
  }

  std::tie(m_rate_scaling_1, m_rate_scaling_2) =
      Meteorology::getScalingRates(m_variables[0]);

  this->process_data();

  const auto r1 = m_gridded1->getVariable1d(m_variables[0]);
  const auto r2 = m_gridded2->getVariable1d(m_variables[0]);

  for (size_t i = 0; i < m_windGrid->ni(); ++i) {
    for (size_t j = 0; j < m_windGrid->nj(); ++j) {
      const auto interp_1 = m_interpolation_1->interpolation().get(i, j);
      const auto interp_2 = m_interpolation_2->interpolation().get(i, j);

      auto valid1 =
          InterpolationWeight::valid(interp_1, Triangulation::invalid_point());
      auto valid2 =
          InterpolationWeight::valid(interp_2, Triangulation::invalid_point());

      if (!valid1 || !valid2) {
        if (this->m_useBackgroundFlag) {
          r.set(0, i, j, MeteorologicalData<1, float>::flag_value());
        } else {
          r.set(0, i, j, 0.0);
        }
      } else {
        const auto w1 = m_interpolation_1->interpolation().get(i, j).weight();
        const auto i1 = m_interpolation_1->interpolation().get(i, j).index();

        const auto w2 = m_interpolation_2->interpolation().get(i, j).weight();
        const auto i2 = m_interpolation_2->interpolation().get(i, j).index();

        const std::array<double, 3> v1 = {r1[i1[0]], r1[i1[1]], r1[i1[2]]};
        const std::array<double, 3> v2 = {r2[i2[0]], r2[i2[1]], r2[i2[2]]};

        const auto r_star1 = InterpolationWeight::interpolate(w1, v1);
        const auto r_star2 = InterpolationWeight::interpolate(w2, v2);

        const auto r_value = (1.0 - time_weight) * r_star1 * m_rate_scaling_1 +
                             time_weight * r_star2 * m_rate_scaling_2;

        r.set(0, i, j, r_value);
      }
    }
  }

  return r;
}

std::tuple<double, double> Meteorology::getScalingRates(
    const GriddedDataTypes::VARIABLES &variable) const {
  const auto scalarVariableName =
      m_gridded1->variableNames().find_variable(m_variables[0]);
  if (scalarVariableName == "apcp" || scalarVariableName == "tp") {
    return {1.0 / static_cast<double>(
                      Grib::getStepLength(m_file1[0], scalarVariableName)),
            1.0 / static_cast<double>(
                      Grib::getStepLength(m_file2[0], scalarVariableName))};
  } else {
    return {1.0, 1.0};
  }
}

MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
Meteorology::to_grid(const double time_weight) {
  if (Meteorology::typeLengthMap(this->m_type) == 1) {
    return {this->scalar_value_interpolation(time_weight)};
  } else {
    metbuild_throw_exception(
        "Invalid field type passed to scalar interpolation");
    return {MetBuild::MeteorologicalData<1, MeteorologicalDataType>()};
  }
}

MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
Meteorology::to_wind_grid(double time_weight) {
  const auto pressure_scaling_1 =
      MetBuild::Meteorology::getPressureScaling(m_gridded1.get());
  const auto pressure_scaling_2 =
      MetBuild::Meteorology::getPressureScaling(m_gridded2.get());

  if (this->m_type != MetBuild::GriddedDataTypes::WIND_PRESSURE) {
    metbuild_throw_exception(
        "Data type must be wind and pressure to interpolate to a wind grid "
        "object");
  }
  MeteorologicalData<3, MetBuild::MeteorologicalDataType> w(m_windGrid->ni(),
                                                            m_windGrid->nj());

  if (time_weight < 0.0) {
    if (this->m_useBackgroundFlag) {
      w.fill(
          MeteorologicalData<3,
                             MetBuild::MeteorologicalDataType>::flag_value());
    } else {
      w.fill_parameter(0, 0.0);
      w.fill_parameter(1, 0.0);
      w.fill_parameter(
          2, MeteorologicalData<
                 3, MetBuild::MeteorologicalDataType>::background_pressure());
    }
    return w;
  }

  this->process_data();

  const auto u1 =
      m_gridded1->getVariable1d(MetBuild::GriddedDataTypes::VAR_U10);
  const auto v1 =
      m_gridded1->getVariable1d(MetBuild::GriddedDataTypes::VAR_V10);
  const auto p1 =
      m_gridded1->getVariable1d(MetBuild::GriddedDataTypes::VAR_PRESSURE);

  const auto u2 =
      m_gridded2->getVariable1d(MetBuild::GriddedDataTypes::VAR_U10);
  const auto v2 =
      m_gridded2->getVariable1d(MetBuild::GriddedDataTypes::VAR_V10);
  const auto p2 =
      m_gridded2->getVariable1d(MetBuild::GriddedDataTypes::VAR_PRESSURE);

  const auto lon = m_gridded1->longitude1d();
  const auto lat = m_gridded1->latitude1d();

  for (size_t i = 0; i < m_windGrid->ni(); ++i) {
    for (size_t j = 0; j < m_windGrid->nj(); ++j) {
      const auto interp_1 = m_interpolation_1->interpolation().get(i, j);
      const auto interp_2 = m_interpolation_2->interpolation().get(i, j);

      const auto valid1 =
          InterpolationWeight::valid(interp_1, Triangulation::invalid_point());
      const auto valid2 =
          InterpolationWeight::valid(interp_2, Triangulation::invalid_point());

      if (!valid1 || !valid2) {
        if (this->m_useBackgroundFlag) {
          w.set(0, i, j,
                MeteorologicalData<3, MeteorologicalDataType>::flag_value());
        } else {
          w.set(0, i, j, 0.0);
          w.set(1, i, j, 0.0);
          w.set(2, i, j,
                MeteorologicalData<
                    3, MeteorologicalDataType>::background_pressure());
        }
      } else {
        const auto w1 = m_interpolation_1->interpolation().get(i, j).weight();
        const auto w2 = m_interpolation_2->interpolation().get(i, j).weight();
        const auto i1 = m_interpolation_1->interpolation().get(i, j).index();
        const auto i2 = m_interpolation_2->interpolation().get(i, j).index();

        const std::array<double, 3> uu1 = {u1[i1[0]], u1[i1[1]], u1[i1[2]]};
        const std::array<double, 3> vv1 = {v1[i1[0]], v1[i1[1]], v1[i1[2]]};
        const std::array<double, 3> pp1 = {p1[i1[0]], p1[i1[1]], p1[i1[2]]};

        const std::array<double, 3> uu2 = {u2[i2[0]], u2[i2[1]], u2[i2[2]]};
        const std::array<double, 3> vv2 = {v2[i2[0]], v2[i2[1]], v2[i2[2]]};
        const std::array<double, 3> pp2 = {p2[i2[0]], p2[i2[1]], p2[i2[2]]};

        const auto u_star1 = InterpolationWeight::interpolate(w1, uu1);
        const auto u_star2 = InterpolationWeight::interpolate(w2, uu2);

        const auto v_star1 = InterpolationWeight::interpolate(w1, vv1);
        const auto v_star2 = InterpolationWeight::interpolate(w2, vv2);

        const auto p_star1 =
            InterpolationWeight::interpolate(w1, pp1) * pressure_scaling_1;
        const auto p_star2 =
            InterpolationWeight::interpolate(w2, pp2) * pressure_scaling_2;

        const auto u_value =
            (1.0 - time_weight) * u_star1 + time_weight * u_star2;
        const auto v_value =
            (1.0 - time_weight) * v_star1 + time_weight * v_star2;
        const auto p_value =
            (1.0 - time_weight) * p_star1 + time_weight * p_star2;

        w.set(0, i, j, u_value);
        w.set(1, i, j, v_value);
        w.set(2, i, j, p_value);
      }
    }
  }
  return w;
}

int Meteorology::write_debug_file(int index) const {
  auto *ptr = index == 0 ? m_gridded1.get() : m_gridded2.get();

  if (ptr == nullptr) {
    metbuild_throw_exception(
        "No available Grib file has been loaded to the specified position");
    return 1;
  }

  const auto lon = ptr->longitude1d();
  const auto lat = ptr->latitude1d();
  const auto u = ptr->getVariable1d(MetBuild::GriddedDataTypes::VAR_U10);
  const auto v = ptr->getVariable1d(MetBuild::GriddedDataTypes::VAR_V10);
  const auto p = ptr->getVariable1d(MetBuild::GriddedDataTypes::VAR_PRESSURE);

  std::ofstream file;
  file.open(ptr->filenames()[0] += ".out");
  for (size_t i = 0; i < lon.size(); ++i) {
    file << lon[i] << " " << lat[i] << " "
         << std::sqrt(std::pow(u[i], 2.0) + std::pow(v[i], 2.0)) << " " << p[i]
         << std::endl;
  }
  file.close();

  return MB_NOERROR;
}

double Meteorology::generate_time_weight(const MetBuild::Date &t1,
                                         const MetBuild::Date &t2,
                                         const MetBuild::Date &t_output) {
  auto s1 = static_cast<double>(t1.toSeconds());
  auto s2 = static_cast<double>(t2.toSeconds());
  auto s3 = static_cast<double>(t_output.toSeconds());
  return (s3 - s1) / (s2 - s1);
}

std::unique_ptr<GriddedData> Meteorology::gridded_data_factory(
    const std::vector<std::string> &filenames,
    const Meteorology::SOURCE source) {
  switch (source) {
    case GFS:
      return std::make_unique<MetBuild::GfsData>(filenames[0]);
    case GEFS:
      return std::make_unique<MetBuild::GefsData>(filenames[0]);
    case NAM:
      return std::make_unique<MetBuild::NamData>(filenames[0]);
    case HWRF:
      return std::make_unique<MetBuild::HwrfData>(filenames[0]);
    case COAMPS:
      return std::make_unique<MetBuild::CoampsData>(filenames);
    default:
      Logging::throwError(
          "No valid source type defined. Cannot create object.");
      return nullptr;
  }
}

double Meteorology::getPressureScaling(const GriddedData *g) {
  if (g->sourceSubtype() == MetBuild::GriddedDataTypes::SOURCE_SUBTYPE::GRIB) {
    return 1.0 / 100.0;
  } else {
    return 1.0;
  }
}
