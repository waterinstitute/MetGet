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
#ifndef METGET_SRC_DATA_SOURCES_HRRRALASKADATA_H_
#define METGET_SRC_DATA_SOURCES_HRRRALASKADATA_H_

#include "Grib.h"

namespace MetBuild {

class HrrrAlaskaData : public Grib {
 public:
  explicit HrrrAlaskaData(const std::string &filename)
      : Grib(filename,
             {"longitudes", "latitudes", "mslma", "10u", "10v", "prate", "2r",
              "2t", "ci"},
             {1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0}, CONVENTION_360) {
    this->get_bounding_region();
  }

  ~HrrrAlaskaData() override = default;

 private:
  void get_bounding_region() {
    const auto x = this->longitude1d();
    const auto y = this->latitude1d();
    std::vector<Point> region;

    const auto longitude = this->longitude1d();
    const auto latitude = this->latitude1d();

    // Bottom Left --> Bottom Right
    for (size_t i = 0; i < ni(); ++i) {
      region.emplace_back(longitude[i], latitude[i]);
    }

    // Bottom Right --> Top Right
    for (size_t i = 1; i < nj(); ++i) {
      region.emplace_back(longitude[i * ni() - 1], latitude[i * ni() - 1]);
    }

    // Top Right --> Top Left
    for (size_t i = 0; i < ni(); ++i) {
      region.emplace_back(longitude[nj() * ni() - 1 - i],
                          latitude[nj() * ni() - 1 - i]);
    }

    // Top Left --> Bottom Left (note: skips last point)
    for (long i = nj() - 1; i > 0; --i) {
      region.emplace_back(longitude[i * ni()], latitude[i * ni()]);
    }

    this->set_bounding_region(region);
    this->write_bounding_region("hrrr_alaska.txt");
  }
};
}  // namespace MetBuild
#endif  // METGET_SRC_DATA_SOURCES_HRRRALASKADATA_H_
