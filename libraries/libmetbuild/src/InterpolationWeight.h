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
#ifndef METGET_SRC_INTERPOLATIONWEIGHT_H_
#define METGET_SRC_INTERPOLATIONWEIGHT_H_

#include <array>
#include <cstdlib>
#include <iostream>

namespace MetBuild {
class InterpolationWeight {
 public:
  InterpolationWeight() = default;

  InterpolationWeight(std::array<size_t, 3> index, std::array<double, 3> weight)
      : m_index(index), m_weight(weight) {}

  [[nodiscard]] const std::array<double, 3> &weight() const { return m_weight; }

  [[nodiscard]] const std::array<size_t, 3> &index() const { return m_index; }

  static bool valid(const InterpolationWeight &w, const size_t check_value) {
    return w.index()[0] != check_value && w.index()[1] != check_value &&
           w.index()[2] != check_value;
  }

  static double interpolate(const std::array<double, 3> &weights,
                            const std::array<double, 3> &values) {
    double v = 0.0;
    for (auto i = 0; i < 3; ++i) {
      v += weights[i] * values[i];
    }
    return v;
  }

  void print() {
    std::cout << std::endl;
    std::cout << "Interpolation weight: " << m_weight[0] << ", " << m_weight[1]
              << ", " << m_weight[2] << std::endl;
    std::cout << " Interpolation index: " << m_index[0] << ", " << m_index[1]
              << ", " << m_index[2] << std::endl;
  }

 private:
  std::array<size_t, 3> m_index;
  std::array<double, 3> m_weight;
};
}  // namespace MetBuild

#endif  // METGET_SRC_INTERPOLATIONWEIGHT_H_
