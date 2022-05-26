//
// Created by Zach Cobell on 5/26/22.
//

#include "InterpolationWeights.h"

#include <cassert>

using namespace MetBuild;

InterpolationWeights::InterpolationWeights(size_t ni, size_t nj)
    : m_weights(std::vector<std::vector<InterpolationWeight>>(
          ni, std::vector<InterpolationWeight>(nj))) {
  assert(ni > 0);
  assert(nj > 0);
}

void InterpolationWeights::set(size_t i, size_t j,
                               const InterpolationWeight &w) {
  m_weights[i][j] = w;
}

const InterpolationWeight &InterpolationWeights::get(size_t i, size_t j) const {
  assert(i < m_weights.size());
  assert(j < m_weights[0].size());
  return m_weights[i][j];
}
size_t InterpolationWeights::ni() const { return m_weights.size(); }

size_t InterpolationWeights::nj() const { return m_weights[0].size(); }
