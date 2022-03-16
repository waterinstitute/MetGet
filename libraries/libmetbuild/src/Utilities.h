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
#ifndef METGET_SRC_UTILITIES_H_
#define METGET_SRC_UTILITIES_H_

#include <limits>
#include <vector>

#include "boost/filesystem.hpp"

namespace MetBuild::Utilities {
template <typename T>
std::vector<T> vector_generate(size_t n, T init = 0, T increment = 1) {
  std::vector<T> v;
  v.reserve(n);
  T value = init;
  for (size_t i = 0; i < n; ++i) {
    v.push_back(value);
    value += increment;
  }
  return v;
}

inline std::string extension(const std::string &file) {
  return boost::filesystem::path(file).extension().string();
}

inline std::string filename(const std::string &file) {
  return boost::filesystem::path(file).filename().string();
}

inline bool exists(const std::string &file) {
  return boost::filesystem::exists(file);
}

template <typename T, typename std::enable_if<
                          std::is_floating_point<T>::value>::type * = nullptr>
constexpr bool equal(const T v1, const T v2) {
  return std::abs(v1 - v2) < std::numeric_limits<T>::epsilon();
}

template <typename T, typename std::enable_if<
                          std::is_floating_point<T>::value>::type * = nullptr>
constexpr bool not_equal(const T v1, const T v2) {
  return !equal(v1, v2);
}

template <typename T, typename std::enable_if<
                          std::is_floating_point<T>::value>::type * = nullptr>
constexpr bool equal_zero(const T v1) {
  return equal(v1, 0.0);
}

template <typename T, typename std::enable_if<
                          std::is_floating_point<T>::value>::type * = nullptr>
constexpr bool not_equal_zero(const T v1) {
  return not_equal(v1, 0.0);
}

void ncCheck(int err);

}  // namespace MetBuild::Utilities
#endif  // METGET_SRC_UTILITIES_H_
