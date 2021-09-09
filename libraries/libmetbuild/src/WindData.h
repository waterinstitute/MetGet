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

  void fill(double u, double v, double p);
  void fill(double value);

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
