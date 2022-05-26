//
// Created by Zach Cobell on 5/26/22.
//

#ifndef METGET_SRC_INTERPOLATIONWEIGHTS_H_
#define METGET_SRC_INTERPOLATIONWEIGHTS_H_

#include <array>
#include <cstdlib>
#include <vector>

#include "InterpolationWeight.h"

namespace MetBuild {
class InterpolationWeights {
 public:
  explicit InterpolationWeights(size_t ni, size_t nj);

  void set(size_t i, size_t j, const InterpolationWeight &w);

  [[nodiscard]] size_t ni() const;
  [[nodiscard]] size_t nj() const;

  [[nodiscard]] const MetBuild::InterpolationWeight &get(size_t i,
                                                         size_t j) const;

 private:
  std::vector<std::vector<MetBuild::InterpolationWeight>> m_weights;
};
}  // namespace MetBuild
#endif  // METGET_SRC_INTERPOLATIONWEIGHTS_H_
