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

#include "Grib.h"
#include "Logging.h"
#include "MetBuild_Status.h"
#include "Utilities.h"

using namespace MetBuild;

Meteorology::Meteorology(const MetBuild::Grid *windGrid, Meteorology::TYPE type,
                         bool backfill)
    : m_type(type),
      m_windGrid(windGrid),
      m_rate_scaling_1(1.0),
      m_rate_scaling_2(1.0),
      m_grib1(nullptr),
      m_grib2(nullptr),
      m_file1(std::string()),
      m_file2(std::string()),
      m_interpolation_1(nullptr),
      m_interpolation_2(nullptr),
      m_useBackgroundFlag(backfill) {}

void Meteorology::set_next_file(const std::string &filename) {
  m_file1 = std::move(m_file2);
  m_file2 = filename;
}

void Meteorology::set_next_file(const char *filename) {
  this->set_next_file(std::string(filename));
}

int Meteorology::process_data() {
  assert(!m_file1.empty());
  assert(!m_file2.empty());

  if (m_file1.empty() || m_file2.empty()) {
    metbuild_throw_exception(
        "Files not specified before attempting to process.");
    return MB_ERROR;
  }

  if (m_grib1 && m_grib2) {
    if (m_file1 == m_grib1->filename() && m_file2 == m_grib2->filename()) {
      return MB_NOERROR;
    }
  }

  if (m_grib2) {
    if (m_grib2->filename() == m_file1) {
      m_grib1.reset(nullptr);
      m_grib1 = std::move(m_grib2);
      m_interpolation_1 = std::move(m_interpolation_2);
    } else {
      m_grib1 = std::make_unique<Grib>(m_file1);
      m_interpolation_1 = std::make_shared<InterpolationWeights>(
          Meteorology::generate_interpolation_weight(m_grib1.get(),
                                                     m_windGrid));
    }
  } else {
    m_grib1 = std::make_unique<Grib>(m_file1);
    m_interpolation_1 = std::make_shared<InterpolationWeights>(
        Meteorology::generate_interpolation_weight(m_grib1.get(), m_windGrid));
  }
  m_grib2 = std::make_unique<Grib>(m_file2);

  if (m_grib1->latitude1d() == m_grib2->latitude1d() &&
      m_grib1->longitude1d() == m_grib2->longitude1d()) {
    m_interpolation_2 =
        std::make_shared<InterpolationWeights>(*m_interpolation_1);
  } else {
    m_interpolation_2 = std::make_shared<InterpolationWeights>(
        Meteorology::generate_interpolation_weight(m_grib2.get(), m_windGrid));
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

  m_scalarVariableName_1 = this->findScalarVariableName(m_file1);
  if (m_scalarVariableName_1 == "apcp" || m_scalarVariableName_1 == "tp") {
    m_rate_scaling_1 = 1.0 / static_cast<double>(Grib::getStepLength(
                                 m_file1, m_scalarVariableName_1));
  }

  m_scalarVariableName_2 = this->findScalarVariableName(m_file2);
  if (m_scalarVariableName_2 == "apcp" || m_scalarVariableName_2 == "tp") {
    m_rate_scaling_2 = 1.0 / static_cast<double>(Grib::getStepLength(
                                 m_file2, m_scalarVariableName_2));
  }

  this->process_data();

  const auto r1 = m_grib1->getGribArray1d(m_scalarVariableName_1);
  const auto r2 = m_grib2->getGribArray1d(m_scalarVariableName_2);

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

  if (this->m_type != Meteorology::WIND_PRESSURE) {
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

  const auto u1 = m_grib1->getGribArray1d("10u");
  const auto v1 = m_grib1->getGribArray1d("10v");
  const auto p1 = m_grib1->getGribArray1d("prmsl");

  const auto u2 = m_grib2->getGribArray1d("10u");
  const auto v2 = m_grib2->getGribArray1d("10v");
  const auto p2 = m_grib2->getGribArray1d("prmsl");

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
    const MetBuild::Grib *grib, const MetBuild::Grid *wind_grid) {
  InterpolationWeights weights;
  weights.resize(wind_grid->ni(), wind_grid->nj());

  for (size_t j = 0; j < wind_grid->nj(); ++j) {
    for (size_t i = 0; i < wind_grid->ni(); ++i) {
      const auto p = wind_grid->corner(i, j);

      if (!grib->point_inside(p)) {
        std::fill(weights.index[j][i].begin(), weights.index[j][i].end(), 0);
        std::fill(weights.weight[j][i].begin(), weights.weight[j][i].end(),
                  0.0);
      } else {
        const auto result =
            grib->kdtree()->findXNearest(p.x(), p.y(), c_idw_depth);

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
  Grib *ptr = index == 0 ? m_grib1.get() : m_grib2.get();

  if (ptr == nullptr) {
    metbuild_throw_exception(
        "No available Grib file has been loaded to the specified position");
    return 1;
  }

  const auto lon = ptr->longitude2d();
  const auto lat = ptr->latitude2d();
  const auto u = ptr->getGribArray2d("10u");
  const auto v = ptr->getGribArray2d("10v");
  const auto p = ptr->getGribArray2d("prmsl");

  std::ofstream file;
  file.open(ptr->filename() += ".out");
  for (size_t i = 0; i < lon.size(); ++i) {
    for (size_t j = 0; j < lon[i].size(); ++j) {
      file << lon[i][j] << " " << lat[i][j] << " "
           << std::sqrt(std::pow(u[i][j], 2.0) + std::pow(v[i][j], 2.0)) << " "
           << p[i][j] << std::endl;
    }
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

std::string Meteorology::findScalarVariableName(const std::string &filename) {
  const auto candidates = [&]() {  // IILE
    switch (m_type) {
      case RAINFALL:
        return std::vector<std::string>{"apcp", "prate", "tp"};
      case TEMPERATURE:
        return std::vector<std::string>{"tmp:30-0 mb above ground",
                                        "tmp:2 m above ground"};
      case HUMIDITY:
        return std::vector<std::string>{"rh:30-0 mb above ground",
                                        "rh:2 m above ground"};
      case ICE:
        return std::vector<std::string>{"ICEC:surface"};
      case WIND_PRESSURE:
        metbuild_throw_exception(
            "Invalid to select WIND_PRESSURE for scalar field");
        return std::vector<std::string>();
      default:
        metbuild_throw_exception("Invalid scalar variable type specified.");
        return std::vector<std::string>();
    }
  }();

  for (const auto &s : candidates) {
    if (Grib::containsVariable(filename, s)) {
      return s;
    }
  }
  metbuild_throw_exception("Variable could not be found in the specified file");
  return std::string();
}
