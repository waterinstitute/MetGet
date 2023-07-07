////////////////////////////////////////////////////////////////////////////////////
// MIT License
//
// Copyright (c) 2023 The Water Institute
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
//
// Author: Zachary Cobell
// Contact: zcobell@thewaterinstitute.org
// Organization: The Water Institute
//
////////////////////////////////////////////////////////////////////////////////////
#ifndef METGET_SRC_DATA_SOURCES_COAMPSDOMAIN_H_
#define METGET_SRC_DATA_SOURCES_COAMPSDOMAIN_H_

#include <memory>
#include <string>
#include <vector>

#include "CppAttributes.h"
#include "Geometry.h"
#include "NetcdfFile.h"
#include "Point.h"

namespace MetBuild {
class CoampsDomain {
 public:
  explicit CoampsDomain(std::string filename);

  NetcdfFile *ncid();

  size_t size() const;

  size_t nlat() const;

  size_t nlon() const;

  double longitude(size_t index) const;

  double latitude(size_t index) const;

  std::array<Point, 4> corners() const;

  MetBuild::Geometry *geometry();

  bool point_inside(const Point &p);

  size_t n_masked_points() const;

  bool masked(size_t index) const;

  void setMask(size_t index, bool value);

  std::array<std::vector<double>, 2> getUnmaskedCoordinates() const;

  std::vector<double> get(const std::string &variable) const;

  [[nodiscard]] const MetBuild::Point &point_ll() const;

  [[nodiscard]] const MetBuild::Point &point_ur() const;

  std::vector<Point> get_bounding_region() const;

 private:
  void initialize();
  void findCorners();

  static double normalize_longitude(double longitude);

  std::string m_filename;
  std::unique_ptr<NetcdfFile> m_ncid;
  int m_dimid_lat;
  int m_dimid_lon;
  size_t m_nlon;
  size_t m_nlat;
  size_t m_mask_count;
  int m_varid_lat;
  int m_varid_lon;
  double m_xll;

  MetBuild::Point m_point_ll;
  MetBuild::Point m_point_ur;

  std::vector<double> m_longitude;
  std::vector<double> m_latitude;
  std::vector<bool> m_mask;

  std::array<MetBuild::Point, 4> m_corners;
};
}  // namespace MetBuild
#endif  // METGET_SRC_DATA_SOURCES_COAMPSDOMAIN_H_
