//
// Created by Zach Cobell on 5/31/22.
//

#include "InterpolationData.h"

using namespace MetBuild;

InterpolationData::InterpolationData(const Triangulation& triangulation,
                                     const MetBuild::Grid::grid& grid)
    : m_triangulation(triangulation),
      m_weights(generate_interpolation_weight(grid)) {}

const InterpolationWeights& InterpolationData::interpolation() const {
  return m_weights;
}

InterpolationWeights& InterpolationData::interpolation() { return m_weights; }

const Triangulation& InterpolationData::triangulation() const {
  return m_triangulation;
}

InterpolationWeights InterpolationData::generate_interpolation_weight(
    const MetBuild::Grid::grid& grid) {
  const auto ni = grid.size();
  const auto nj = grid[0].size();
  InterpolationWeights weights(nj, ni);
  for (size_t i = 0; i < ni; ++i) {
    for (size_t j = 0; j < nj; ++j) {
      auto p = grid[i][j];
      p.setX((std::fmod(p.x() + 180.0, 360.0)) - 180.0);
      auto iw = m_triangulation.getInterpolationFactors(p.x(), p.y());
      weights.set(j, i, iw);
    }
  }
  return weights;
}