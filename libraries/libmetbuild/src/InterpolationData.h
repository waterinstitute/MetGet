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
#ifndef METGET_SRC_INTERPOLATIONDATA_H_
#define METGET_SRC_INTERPOLATIONDATA_H_

#include "CoordinateConvention.h"
#include "Grid.h"
#include "InterpolationWeights.h"
#include "Triangulation.h"

namespace MetBuild {

class InterpolationData {
 public:
  InterpolationData(const Triangulation &triangulation,
                    const MetBuild::Grid::grid &grid,
                    COORDINATE_CONVENTION convention = CONVENTION_180);

  [[nodiscard]] const InterpolationWeights &interpolation() const;
  InterpolationWeights &interpolation();

  [[nodiscard]] const Triangulation &triangulation() const;

  [[nodiscard]] COORDINATE_CONVENTION convention() const;

 private:
  InterpolationWeights generate_interpolation_weight(
      const MetBuild::Grid::grid &grid);

  Triangulation m_triangulation;
  InterpolationWeights m_weights;
  COORDINATE_CONVENTION m_convention;
};
}  // namespace MetBuild
#endif  // METGET_SRC_INTERPOLATIONDATA_H_
