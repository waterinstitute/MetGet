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
#ifndef METGET_SRC_DATA_SOURCES_COAMPSDOMAIN_H_
#define METGET_SRC_DATA_SOURCES_COAMPSDOMAIN_H_

#include <memory>
#include <string>
#include <vector>

#include "CppAttributes.h"
#include "NetcdfFile.h"

namespace MetBuild {
class CoampsDomain {
 public:
  explicit CoampsDomain(std::string filename);

 private:
  void initialize();

  std::string m_filename;
  std::unique_ptr<NetcdfFile> m_ncid;
  int m_dimid_lat;
  int m_dimid_lon;
  size_t m_nlon;
  size_t m_nlat;
  int m_varid_lat;
  int m_varid_lon;
  int m_varid_press;
  int m_varid_uwind;
  int m_varid_vwind;
  int m_varid_rh;
  int m_varid_temp;

  std::vector<double> m_longitude;
  std::vector<double> m_latitude;

};
}  // namespace MetBuild
#endif  // METGET_SRC_DATA_SOURCES_COAMPSDOMAIN_H_
