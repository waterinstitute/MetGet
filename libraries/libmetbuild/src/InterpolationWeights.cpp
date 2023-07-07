////////////////////////////////////////////////////////////////////////////////////
// MIT License
//
// Copyright (c) 2023 The Water Institute
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// Author: Zachary Cobell
// Contact: zcobell@thewaterinstitute.org
// Organization: The Water Institute
//
////////////////////////////////////////////////////////////////////////////////////
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
