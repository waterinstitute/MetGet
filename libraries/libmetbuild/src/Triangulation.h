//
// Created by Zach Cobell on 5/31/22.
//

#ifndef METGET_SRC_TRIANGULATION_H_
#define METGET_SRC_TRIANGULATION_H_

#include <limits>
#include <memory>
#include <vector>

#include "InterpolationWeight.h"
#include "Point.h"

namespace MetBuild {
namespace Private {
class TriangulationPrivate;
}
class Triangulation {
 public:
  Triangulation(const std::vector<double> &x, const std::vector<double> &y,
                const std::vector<MetBuild::Point> &bounding_region);

  ~Triangulation();

  Triangulation(const Triangulation &t);

  static constexpr size_t invalid_point() {
    return std::numeric_limits<size_t>::max();
  }

  [[nodiscard]] MetBuild::InterpolationWeight getInterpolationFactors(
      double x, double y) const;

 private:
  std::unique_ptr<Private::TriangulationPrivate> m_ptr;
};

}  // namespace MetBuild
#endif  // METGET_SRC_TRIANGULATION_H_
