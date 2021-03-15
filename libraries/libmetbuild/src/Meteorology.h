#ifndef METBUILD_METEOROLOGY_H
#define METBUILD_METEOROLOGY_H

#include <memory>
#include <string>

#include "Date.h"
#include "Grib.h"
#include "MetBuild_Global.h"
#include "WindData.h"
#include "WindGrid.h"

namespace MetBuild {

class Meteorology {
 public:
  METBUILD_EXPORT explicit Meteorology(const MetBuild::WindGrid *grid);

  METBUILD_EXPORT void set_next_file(const std::string &filename);
  METBUILD_EXPORT void set_next_file(const char *filename);

  int METBUILD_EXPORT process_data();

  int METBUILD_EXPORT write_debug_file(int index) const;

  MetBuild::WindData METBUILD_EXPORT to_wind_grid(double time_weight = 1.0);

  static double METBUILD_EXPORT generate_time_weight(const MetBuild::Date &t1, const MetBuild::Date &t2, const MetBuild::Date &t_output); 

 private:
  constexpr static double epsilon_squared() {
    return std::numeric_limits<double>::epsilon() *
           std::numeric_limits<double>::epsilon();
  }
  constexpr static size_t c_idw_depth = 6;
  struct InterpolationWeights {
    std::vector<std::array<double, c_idw_depth>> weight;
    std::vector<std::array<unsigned, c_idw_depth>> index;
    void resize(size_t sz) {
      weight.resize(sz);
      index.resize(sz);
    };
  };

  static InterpolationWeights generate_interpolation_weight(
      const MetBuild::Grib *grib, const MetBuild::WindGrid *wind_grid);

  const WindGrid *m_windGrid;
  std::unique_ptr<Grib> m_grib1;
  std::unique_ptr<Grib> m_grib2;
  std::string m_file1;
  std::string m_file2;
  std::shared_ptr<InterpolationWeights> m_interpolation_1;
  std::shared_ptr<InterpolationWeights> m_interpolation_2;
};
}  // namespace MetBuild
#endif  // METBUILD_METEOROLOGY_H
