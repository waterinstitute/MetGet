
#ifndef METGET_SRC_UTILITIES_H_
#define METGET_SRC_UTILITIES_H_

#include <vector>

#include "boost/filesystem.hpp"

namespace MetGetUtility {
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

}  // namespace MetGetUtility

#endif  // METGET_SRC_UTILITIES_H_
