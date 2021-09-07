//
// Created by Zach Cobell on 1/21/21.
//

#ifndef METGET_LIBRARY_WINDDATA_H_
#define METGET_LIBRARY_WINDDATA_H_

#include <array>
#include <vector>

namespace MetBuild {

class WindData {
 public:
  explicit WindData(size_t ni, size_t nj);

  static constexpr double background_pressure() { return 1013.0; }
  static constexpr double flag_value() { return -999.0; }

  const std::vector<std::vector<double>> &u() const;
  const std::vector<std::vector<double>> &v() const;
  const std::vector<std::vector<double>> &p() const;

  constexpr size_t ni() const { return m_ni; }
  constexpr size_t nj() const { return m_nj; }

  void setU(size_t i, size_t j, double value);
  void setV(size_t i, size_t j, double value);
  void setP(size_t i, size_t j, double value);

 private:
  size_t m_ni;
  size_t m_nj;
  std::vector<std::vector<double>> m_u;
  std::vector<std::vector<double>> m_v;
  std::vector<std::vector<double>> m_p;
};

}  // namespace MetBuild

#endif  // METGET_LIBRARY_WINDDATA_H_
