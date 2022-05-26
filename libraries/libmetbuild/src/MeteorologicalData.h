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
#ifndef METGET_SRC_METEOROLOGICALDATA_H_
#define METGET_SRC_METEOROLOGICALDATA_H_

#include <array>
#include <cassert>
#include <vector>

#include "CppAttributes.h"

namespace MetBuild {

#define METBUILD_USE_FLOAT
#ifdef METBUILD_USE_FLOAT
using MeteorologicalDataType = float;
#else
using MeteorologicalDataType = double;
#endif

template <unsigned parameters, typename T = MeteorologicalDataType>
class MeteorologicalData {
 public:
  explicit MeteorologicalData(const size_t ni = 0, const size_t nj = 0)
      : m_ni(ni), m_nj(nj) {
    this->resize(m_ni, m_nj);
  }

  virtual ~MeteorologicalData() = default;

  NODISCARD static constexpr T background_pressure() { return 1013.0; }

  NODISCARD static constexpr T flag_value() { return -999.0; }

  NODISCARD size_t ni() const { return m_ni; }

  NODISCARD size_t nj() const { return m_nj; };

  void resize(const size_t ni, const size_t nj) {
    m_ni = ni;
    m_nj = nj;
    for (auto &v : m_data) {
      v.resize(m_nj);
      for (auto &vv : v) {
        vv.resize(m_ni);
        std::fill(vv.begin(), vv.end(),
                  MeteorologicalData<parameters, T>::flag_value());
      }
    }
  }

  NODISCARD const std::vector<std::vector<T>> &operator[](
      const size_t index) const {
    assert(index < parameters);
    return m_data[index];
  }

  NODISCARD std::vector<T> toVector(const size_t index) const {
    assert(index < parameters);
    std::vector<T> v;
    v.reserve(m_ni * m_nj);
    for (const auto &r : m_data[index]) {
      for (const auto c : r) {
        v.push_back(c);
      }
    }
    return v;
  }

  NODISCARD std::vector<std::vector<T>> &operator[](const size_t index) {
    assert(index < parameters);
    return m_data[index];
  }

  virtual void fill(const T value) { this->fill_all(value); }

  void fill_parameter(const size_t index, const T value) {
    assert(index < parameters);
    for (auto &v : m_data[index]) {
      std::fill(v.begin(), v.end(), value);
    }
  }

  void fill_all(const T value = flag_value()) {
    for (auto &v : m_data) {
      for (auto &vv : v) {
        std::fill(vv.begin(), vv.end(), value);
      }
    }
  }

  void set(const size_t parameter, const size_t i, const size_t j,
           const double value) {
    assert(parameter < parameters);
    assert(i < m_ni);
    assert(j < m_nj);
    m_data[parameter][j][i] = value;
  }

  NODISCARD T get(const size_t parameter, const size_t i,
                  const size_t j) const {
    assert(parameter < parameters);
    assert(i < m_ni);
    assert(j < m_nj);
    return m_data[parameter][i][j];
  }

  NODISCARD std::array<T, parameters> getPack(const size_t i,
                                              const size_t j) const {
    std::array<T, parameters> out;
    assert(i < m_ni);
    assert(j < m_nj);
    for (size_t p = 0; p < parameters; ++p) {
      out[p] = m_data[p][i][j];
    }
    return out;
  }

  void setPack(const size_t i, const size_t j,
               const std::array<T, parameters> data) {
    assert(data.size() == parameters);
    assert(i < m_ni);
    assert(j < m_nj);
    for (size_t p = 0; p < parameters; ++p) {
      m_data[p][i][j] = data[p];
    }
  }

  NODISCARD constexpr size_t nParameters() const { return parameters; }

 protected:
#ifndef SWIG
  template <unsigned size, typename T_in, typename T_out>
  static auto recast(const MeteorologicalData<size, T_in> &value) {
    MeteorologicalData<size, T_out> v(value.ni(), value.nj());
    for (auto i = 0; i < value.ni(); ++i) {
      for (auto j = 0; j < value.nj(); ++j) {
        auto f = value.getPack(i, j);
        std::array<T_out, size> ff;
        for (auto k = 0; k < size; ++k) {
          ff[k] = static_cast<T_out>(f[k]);
        }
        v.setPack(i, j, ff);
      }
    }
    return v;
  }
#endif

 private:
  size_t m_ni;
  size_t m_nj;
  std::array<std::vector<std::vector<T>>, parameters> m_data;
};

}  // namespace MetBuild

// template class
// MetBuild::MeteorologicalData<1,MetBuild::MeteorologicalDataType>; template
// class MetBuild::MeteorologicalData<2,MetBuild::MeteorologicalDataType>;
// template class
// MetBuild::MeteorologicalData<3,MetBuild::MeteorologicalDataType>;

#endif  // METGET_SRC_METEOROLOGICALDATA_H_
