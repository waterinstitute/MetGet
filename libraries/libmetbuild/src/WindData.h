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
  explicit WindData(size_t n);

  static constexpr double background_pressure() { return 1013.0; }

  const std::vector<double> &u() const;
  const std::vector<double> &v() const;
  const std::vector<double> &p() const;
  size_t size() const;

  void setU(size_t index, double value);
  void setV(size_t index, double value);
  void setP(size_t index, double value);

 private:
  size_t m_n;
  std::vector<double> m_u;
  std::vector<double> m_v;
  std::vector<double> m_p;
};

}  // namespace MetBuild

#endif  // METGET_LIBRARY_WINDDATA_H_
