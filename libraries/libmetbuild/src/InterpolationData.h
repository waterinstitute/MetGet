//
// Created by Zach Cobell on 5/31/22.
//

#ifndef METGET_SRC_INTERPOLATIONDATA_H_
#define METGET_SRC_INTERPOLATIONDATA_H_

#include "Grid.h"
#include "InterpolationWeights.h"
#include "Triangulation.h"

namespace MetBuild {

class InterpolationData {
 public:
  InterpolationData(const Triangulation &triangulation,
                    const MetBuild::Grid::grid &grid);

  [[nodiscard]] const InterpolationWeights &interpolation() const;
  InterpolationWeights &interpolation();

  [[nodiscard]] const Triangulation &triangulation() const;

 private:
  InterpolationWeights generate_interpolation_weight(
      const MetBuild::Grid::grid &grid);

  Triangulation m_triangulation;
  InterpolationWeights m_weights;
};
}  // namespace MetBuild
#endif  // METGET_SRC_INTERPOLATIONDATA_H_
