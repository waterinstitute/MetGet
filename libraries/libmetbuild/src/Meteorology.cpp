
#include "Meteorology.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <utility>

#include "Grib.h"
#include "Logging.h"
#include "MetBuild_Status.h"
#include "mettypes.h"

using namespace MetBuild;

Meteorology::Meteorology(const WindGrid *windGrid)
    : m_windGrid(windGrid),
      m_file1(std::string()),
      m_file2(std::string()),
      m_grib1(nullptr),
      m_grib2(nullptr),
      m_interpolation_1(nullptr),
      m_interpolation_2(nullptr) {}

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
    m_interpolation_2 = std::make_shared<InterpolationWeights>(*m_interpolation_1);
  } else {
    m_interpolation_2 = std::make_shared<InterpolationWeights>(
      Meteorology::generate_interpolation_weight(m_grib2.get(), m_windGrid));
  }

  return MB_NOERROR;
}

MetBuild::WindData Meteorology::to_wind_grid(double time_weight) {

  this->process_data();
  
  WindData w(m_windGrid->ni(), m_windGrid->nj());

  const auto u1 = m_grib1->getGribArray1d("10u");
  const auto v1 = m_grib1->getGribArray1d("10v");
  const auto p1 = m_grib1->getGribArray1d("prmsl");

  const auto u2 = m_grib2->getGribArray1d("10u");
  const auto v2 = m_grib2->getGribArray1d("10v");
  const auto p2 = m_grib2->getGribArray1d("prmsl");

  std::cout << "Time Weight: " << time_weight << std::endl;

  for (auto i = 0; i < m_windGrid->ni(); ++i) {
    for (auto j = 0; j < m_windGrid->nj(); ++j) {

      if (m_interpolation_1->index[i][j][0] == 0 ||
          m_interpolation_2->index[i][j][0] == 0 ||
          m_interpolation_1->weight[i][j][0] == 0.0 ||
          m_interpolation_2->weight[i][j][0] == 0.0) {
        w.setU(i, j, 0.0);
        w.setV(i, j, 0.0);
        w.setP(i, j, WindData::background_pressure());
      } else {
        double u_star = 0.0;
        double v_star = 0.0;
        double p_star = 0.0;
        double u_star1 = 0.0;
        double v_star1 = 0.0;
        double p_star1 = 0.0;
        double u_star2 = 0.0;
        double v_star2 = 0.0;
        double p_star2 = 0.0;
        double w1_sum = 0.0;
        double w2_sum = 0.0;
        for (auto k = 0; k < c_idw_depth; ++k) {
          const auto idx1 = m_interpolation_1->index[i][j][k];
          const auto idx2 = m_interpolation_2->index[i][j][k];
          const auto w1 = m_interpolation_1->weight[i][j][k];
          const auto w2 = m_interpolation_2->weight[i][j][k];
          u_star1 += w1 * u1[idx1];
          u_star2 += w2 * u2[idx2];
          v_star1 += w1 * v1[idx1];
          v_star2 += w2 * v2[idx2];
          p_star1 += w1 * p1[idx1];
          p_star2 += w2 * p2[idx2];
          w1_sum += w1;
          w2_sum += w2;
        }

        if(w1_sum == 0.0 && w2_sum == 0.0){
          w.setU(i, j, 0.0);
          w.setV(i, j, 0.0);
          w.setP(i, j, WindData::background_pressure()); 
        } else if (w1_sum == 0.0 && w2_sum != 0.0){
          w.setU(i, j, u_star2 * ( 1.0 / w2_sum ));
          w.setV(i, j, v_star2 * ( 1.0 / w2_sum ));
          w.setP(i, j, p_star2 * ( 1.0 / w2_sum ) / 100.0);  // .. Convert to mb
        } else if (w1_sum != 0.0 && w2_sum == 0.0){
          w.setU(i, j, u_star1 * ( 1.0 / w1_sum ) );
          w.setV(i, j, v_star1 * ( 1.0 / w1_sum ));
          w.setP(i, j, p_star1 * ( 1.0 / w2_sum ) / 100.0);  // .. Convert to mb
        } else {
          w.setU(i, j, (1.0 - time_weight) * u_star1 + time_weight * u_star2 );
          w.setV(i, j, (1.0 - time_weight) * v_star1 + time_weight * v_star2 );
          w.setP(i, j, ((1.0 - time_weight) * p_star1 + time_weight * p_star2) / 100.0); // .. Convert to mb
        }
      }
    }
  }
  return w;
}

Meteorology::InterpolationWeights Meteorology::generate_interpolation_weight(
    const MetBuild::Grib *grib, const MetBuild::WindGrid *wind_grid) {
  const auto &g = wind_grid->grid_positions();

  InterpolationWeights weights;
  weights.resize(wind_grid->ni(), wind_grid->nj());

  for (auto i = 0; i < wind_grid->ni(); ++i) {
    for (auto j = 0; j < wind_grid->nj(); ++j) {
      const auto p = wind_grid->corner(i, j);

      if (!grib->point_inside(p)) {
        std::fill(weights.index[i][j].begin(), weights.index[i][j].end(), 0);
        std::fill(weights.weight[i][j].begin(), weights.weight[i][j].end(),
                  0.0);
      } else {
        const auto result =
            grib->kdtree()->findXNearest(p.x(), p.y(), c_idw_depth);

        if (result[0].second < Meteorology::epsilon_squared()) {
          std::fill(weights.index[i][j].begin(), weights.index[i][j].end(),
                    result[0].first);
          std::fill(weights.weight[i][j].begin() + 1,
                    weights.weight[i][j].end(), 0.0);
          weights.weight[i][j][0] = 1.0;
        } else {
          double w_total = 0.0;
          for (auto k = 0; k < c_idw_depth; ++k) {
            weights.weight[i][j][k] = 1.0 / result[k].second;
            w_total += 1.0 / result[k].second;
            weights.index[i][j][k] = result[k].first;
          }
          for (auto &w : weights.weight[i][j]) {
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
  double s1 = static_cast<double>(t1.toSeconds());
  double s2 = static_cast<double>(t2.toSeconds());
  double s3 = static_cast<double>(t_output.toSeconds());
  return (s3 - s1) / (s2 - s1);
}
