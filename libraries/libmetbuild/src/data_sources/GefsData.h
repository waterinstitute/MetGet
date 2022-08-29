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
#ifndef METGET_SRC_GEFSDATA_H_
#define METGET_SRC_GEFSDATA_H_

#include "Grib.h"

namespace MetBuild {

class GefsData : public Grib {
 public:
  explicit GefsData(const std::string &filename)
      : Grib(filename, {"longitudes", "latitudes", "prmsl", "10u", "10v",
                        "", "r2", "t2", ""}) {
    this->get_bounding_region();
  }

  ~GefsData() override = default;

 private:
  void get_bounding_region() {
    const auto x = this->longitude1d();
    const auto y = this->latitude1d();
    std::vector<Point> region;

    std::vector<double> top;
    for (size_t i = 0; i < ni(); ++i) {
      top.push_back(x[i]);
    }
    std::sort(top.begin(), top.end());
    for (const auto &v : top) {
      region.emplace_back(v, 90.0);
    }

    std::vector<double> right;
    for (size_t i = 0; i < nj(); ++i) {
      right.push_back(y[i * ni()]);
    }

    for (const auto &v : right) {
      region.emplace_back(179.75, v);
    }

    for (auto it = top.rbegin(); it != top.rend(); ++it) {
      region.emplace_back(*(it), -90);
    }

    for (auto it = right.rbegin(); it != right.rend(); ++it) {
      region.emplace_back(-180.0, *(it));
    }

    this->set_bounding_region(region);
  }
};
}  // namespace MetBuild
#endif  // METGET_SRC_GEFSDATA_H_
