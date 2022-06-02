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
