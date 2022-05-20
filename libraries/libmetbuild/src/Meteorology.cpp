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

#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <utility>

#include "Logging.h"
#include "MetBuild_Status.h"
#include "Projection.h"
#include "Utilities.h"
#include "data_sources/GfsData.h"
#include "data_sources/Grib.h"
#include "data_sources/HwrfData.h"
#include "data_sources/NamData.h"

using namespace MetBuild;

Meteorology::Meteorology(const MetBuild::Grid *windGrid,
                         Meteorology::SOURCE source, GriddedData::TYPE type,
                         bool backfill, int epsg_output)
    : m_type(type),
      m_source(source),
      m_windGrid(windGrid),
      m_rate_scaling_1(1.0),
      m_rate_scaling_2(1.0),
      m_gridded1(nullptr),
      m_gridded2(nullptr),
      m_interpolation_1(nullptr),
      m_interpolation_2(nullptr),
      m_useBackgroundFlag(backfill),
      m_epsg_output(epsg_output),
      m_grid_positions(m_windGrid->grid_positions()),
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
      m_gridded1 = this->gridded_data_factory(m_file1, m_source);
      m_interpolation_1 = std::make_shared<InterpolationWeights>(
          Meteorology::generate_interpolation_weight(m_gridded1.get(),
                                                     &m_grid_positions));
    }
  } else {
    m_gridded1 = this->gridded_data_factory(m_file1, m_source);
    m_interpolation_1 = std::make_shared<InterpolationWeights>(
        Meteorology::generate_interpolation_weight(m_gridded1.get(),
                                                   &m_grid_positions));
  }
  m_gridded2 = this->gridded_data_factory(m_file2, m_source);

  if (m_gridded1->latitude1d() == m_gridded2->latitude1d() &&
      m_gridded1->longitude1d() == m_gridded2->longitude1d()) {
    m_interpolation_2 =
        std::make_shared<InterpolationWeights>(*m_interpolation_1);
  } else {
    m_interpolation_2 = std::make_shared<InterpolationWeights>(
        Meteorology::generate_interpolation_weight(m_gridded2.get(),
                                                   &m_grid_positions));
  }

  return MB_NOERROR;
}

MetBuild::MeteorologicalData<1> Meteorology::scalar_value_interpolation(
    const double time_weight) {
  using namespace MetBuild::Utilities;

  MeteorologicalData<1> r(m_windGrid->ni(), m_windGrid->nj());

  if (time_weight < 0.0) {
    if (this->m_useBackgroundFlag) {
      r.fill(MeteorologicalData<1>::flag_value());
    } else {
      r.fill(0.0);
    }
    return r;
  }

  // TODO: Need to reintroduce scaling value
  //  m_scalarVariableName_1 = this->findScalarVariableName(m_file1);
  //  if (m_scalarVariableName_1 == "apcp" || m_scalarVariableName_1 == "tp") {
  //    m_rate_scaling_1 = 1.0 / static_cast<double>(Grib::getStepLength(
  //                                 m_file1, m_scalarVariableName_1));
  //  }
  //
  //  m_scalarVariableName_2 = this->findScalarVariableName(m_file2);
  //  if (m_scalarVariableName_2 == "apcp" || m_scalarVariableName_2 == "tp") {
  //    m_rate_scaling_2 = 1.0 / static_cast<double>(Grib::getStepLength(
  //                                 m_file2, m_scalarVariableName_2));
  //  }

  this->process_data();

  const auto r1 = m_gridded1->getVariable1d(m_variables[0]);
  const auto r2 = m_gridded2->getVariable1d(m_variables[0]);

  for (size_t j = 0; j < m_windGrid->nj(); ++j) {
    for (size_t i = 0; i < m_windGrid->ni(); ++i) {
      if (m_interpolation_1->index[j][i][0] == 0 ||
          m_interpolation_2->index[j][i][0] == 0 ||
          m_interpolation_1->weight[j][i][0] == 0.0 ||
          m_interpolation_2->weight[j][i][0] == 0.0) {
        if (this->m_useBackgroundFlag) {
          r.set(0, i, j, MeteorologicalData<1, float>::flag_value());
        } else {
          r.set(0, i, j, 0.0);
        }
      } else {
        double r_star1 = 0.0;
        double r_star2 = 0.0;
        double w1_sum = 0.0;
        double w2_sum = 0.0;
        for (size_t k = 0; k < c_idw_depth; ++k) {
          auto idx1 = m_interpolation_1->index[j][i][k];
          auto idx2 = m_interpolation_2->index[j][i][k];
          auto w1 = m_interpolation_1->weight[j][i][k];
          auto w2 = m_interpolation_2->weight[j][i][k];
          r_star1 += w1 * r1[idx1];
          r_star2 += w2 * r2[idx2];
          w1_sum += w1;
          w2_sum += w2;
        }

        if (equal_zero(w1_sum) && equal_zero(w2_sum)) {
          r.set(0, i, j, 0.0);
        } else if (equal_zero(w1_sum) && not_equal_zero(w2_sum)) {
          r.set(0, i, j, r_star2 * (1.0 / w2_sum) * m_rate_scaling_2);
        } else if (not_equal_zero(w1_sum) && equal_zero(w2_sum)) {
          r.set(0, i, j, r_star1 * (1.0 / w1_sum) * m_rate_scaling_1);
        } else {
          r.set(0, i, j,
                ((1.0 - time_weight) * (r_star1 * m_rate_scaling_1) +
                 time_weight * (r_star2 * m_rate_scaling_2)));
        }
      }
    }
  }

  return r;
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
  using namespace MetBuild::Utilities;

  if (this->m_type != GriddedData::WIND_PRESSURE) {
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

  const auto u1 = m_gridded1->getVariable1d(GriddedData::VAR_U10);
  const auto v1 = m_gridded1->getVariable1d(GriddedData::VAR_V10);
  const auto p1 = m_gridded1->getVariable1d(GriddedData::VAR_PRESSURE);

  const auto u2 = m_gridded2->getVariable1d(GriddedData::VAR_U10);
  const auto v2 = m_gridded2->getVariable1d(GriddedData::VAR_V10);
  const auto p2 = m_gridded2->getVariable1d(GriddedData::VAR_PRESSURE);

  for (size_t j = 0; j < m_windGrid->nj(); ++j) {
    for (size_t i = 0; i < m_windGrid->ni(); ++i) {
      if (m_interpolation_1->index[j][i][0] == 0 ||
          m_interpolation_2->index[j][i][0] == 0 ||
          m_interpolation_1->weight[j][i][0] == 0.0 ||
          m_interpolation_2->weight[j][i][0] == 0.0) {
        if (this->m_useBackgroundFlag) {
          w.set(0, i, j,
                MeteorologicalData<3, MeteorologicalDataType>::flag_value());
          w.set(1, i, j,
                MeteorologicalData<3, MeteorologicalDataType>::flag_value());
          w.set(2, i, j,
                MeteorologicalData<3, MeteorologicalDataType>::flag_value());
        } else {
          w.set(0, i, j, 0.0);
          w.set(1, i, j, 0.0);
          w.set(2, i, j,
                MeteorologicalData<3, MeteorologicalDataType>::flag_value());
        }
      } else {
        double u_star1 = 0.0;
        double v_star1 = 0.0;
        double p_star1 = 0.0;
        double u_star2 = 0.0;
        double v_star2 = 0.0;
        double p_star2 = 0.0;
        double w1_sum = 0.0;
        double w2_sum = 0.0;
        for (size_t k = 0; k < c_idw_depth; ++k) {
          auto idx1 = m_interpolation_1->index[j][i][k];
          auto idx2 = m_interpolation_2->index[j][i][k];
          auto w1 = m_interpolation_1->weight[j][i][k];
          auto w2 = m_interpolation_2->weight[j][i][k];
          u_star1 += w1 * u1[idx1];
          u_star2 += w2 * u2[idx2];
          v_star1 += w1 * v1[idx1];
          v_star2 += w2 * v2[idx2];
          p_star1 += w1 * p1[idx1];
          p_star2 += w2 * p2[idx2];
          w1_sum += w1;
          w2_sum += w2;
        }

        if (equal_zero(w1_sum) && equal_zero(w2_sum)) {
          w.set(0, i, j, 0.0);
          w.set(1, i, j, 0.0);
          w.set(2, i, j,
                MeteorologicalData<
                    3, MeteorologicalDataType>::background_pressure());
        } else if (equal_zero(w1_sum) && not_equal_zero(w2_sum)) {
          w.set(0, i, j,
                static_cast<MeteorologicalDataType>(u_star2 * (1.0 / w2_sum)));
          w.set(1, i, j,
                static_cast<MeteorologicalDataType>(v_star2 * (1.0 / w2_sum)));
          w.set(2, i, j,
                static_cast<MeteorologicalDataType>(
                    p_star2 * (1.0 / w2_sum) / 100.0));  // .. Convert to mb
        } else if (not_equal_zero(w1_sum) && equal_zero(w2_sum)) {
          w.set(0, i, j,
                static_cast<MeteorologicalDataType>(u_star1 * (1.0 / w1_sum)));
          w.set(1, i, j,
                static_cast<MeteorologicalDataType>(v_star1 * (1.0 / w1_sum)));
          w.set(2, i, j,
                static_cast<MeteorologicalDataType>(
                    p_star1 * (1.0 / w2_sum) / 100.0));  // .. Convert to mb
        } else {
          w.set(0, i, j,
                static_cast<MeteorologicalDataType>(
                    (1.0 - time_weight) * u_star1 + time_weight * u_star2));
          w.set(1, i, j,
                static_cast<MeteorologicalDataType>(
                    (1.0 - time_weight) * v_star1 + time_weight * v_star2));
          w.set(2, i, j,
                static_cast<MeteorologicalDataType>(
                    ((1.0 - time_weight) * p_star1 + time_weight * p_star2) /
                    100.0));  // .. Convert to mb
        }
      }
    }
  }
  return w;
}

Meteorology::InterpolationWeights Meteorology::generate_interpolation_weight(
    const MetBuild::GriddedData *gridded, const MetBuild::Grid::grid *grid) {
  InterpolationWeights weights;
  const auto ni = grid->at(0).size();
  const auto nj = grid->size();
  weights.resize(ni, nj);

  for (size_t j = 0; j < nj; ++j) {
    for (size_t i = 0; i < ni; ++i) {
      auto p = grid->at(j)[i];
      p.setX((std::fmod(p.x() + 180.0, 360.0)) - 180.0);

      if (!gridded->point_inside(p)) {
        std::fill(weights.index[j][i].begin(), weights.index[j][i].end(), 0);
        std::fill(weights.weight[j][i].begin(), weights.weight[j][i].end(),
                  0.0);
      } else {
        const auto result =
            gridded->kdtree()->findXNearest(p.x(), p.y(), c_idw_depth);

        if (result[0].second < Meteorology::epsilon_squared()) {
          std::fill(weights.index[j][i].begin(), weights.index[j][i].end(),
                    result[0].first);
          std::fill(weights.weight[j][i].begin() + 1,
                    weights.weight[j][i].end(), 0.0);
          weights.weight[j][i][0] = 1.0;
        } else {
          double w_total = 0.0;
          for (size_t k = 0; k < c_idw_depth; ++k) {
            weights.weight[j][i][k] = 1.0 / result[k].second;
            w_total += 1.0 / result[k].second;
            weights.index[j][i][k] = result[k].first;
          }
          for (auto &w : weights.weight[j][i]) {
            w = w / w_total;
          }
        }
      }
    }
  }
  return weights;
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
  const auto u = ptr->getVariable1d(GriddedData::VAR_U10);
  const auto v = ptr->getVariable1d(GriddedData::VAR_V10);
  const auto p = ptr->getVariable1d(GriddedData::VAR_PRESSURE);

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

// std::string Meteorology::findScalarVariableName(const std::string &filename)
// {
//   const auto candidates = [&]() {  // IILE
//     switch (m_type) {
//       case RAINFALL:
//         return std::vector<std::string>{"apcp", "prate", "tp"};
//       case TEMPERATURE:
//         return std::vector<std::string>{"tmp:30-0 mb above ground",
//                                         "tmp:2 m above ground"};
//       case HUMIDITY:
//         return std::vector<std::string>{"rh:30-0 mb above ground",
//                                         "rh:2 m above ground"};
//       case ICE:
//         return std::vector<std::string>{"ICEC:surface"};
//       case WIND_PRESSURE:
//         metbuild_throw_exception(
//             "Invalid to select WIND_PRESSURE for scalar field");
//         return std::vector<std::string>();
//       default:
//         metbuild_throw_exception("Invalid scalar variable type specified.");
//         return std::vector<std::string>();
//     }
//   }();
//
//   for (const auto &s : candidates) {
//     if (Grib::containsVariable(filename, s)) {
//       return s;
//     }
//   }
//   metbuild_throw_exception("Variable could not be found in the specified
//   file"); return {};
// }

std::unique_ptr<GriddedData> Meteorology::gridded_data_factory(
    const std::vector<std::string> &filenames,
    const Meteorology::SOURCE source) {
  switch (source) {
    case GFS:
      return std::make_unique<MetBuild::GfsData>(filenames[0]);
    case NAM:
      return std::make_unique<MetBuild::NamData>(filenames[0]);
    case HWRF:
      return std::make_unique<MetBuild::HwrfData>(filenames[0]);
    case COAMPS:
      return nullptr;
    default:
      Logging::throwError(
          "No valid source type defined. Cannot create object.");
      return nullptr;
  }
}
