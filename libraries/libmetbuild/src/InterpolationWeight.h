//
// Created by Zach Cobell on 5/26/22.
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
