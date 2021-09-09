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
#ifndef METGET_SRC_NCFILE_H_
#define METGET_SRC_NCFILE_H_

#include <string>
#include <vector>

class NcFile {
 public:
  struct NcGroup {
    NcGroup()
        : grpid(0),
          dimid_time(0),
          dimid_xi(0),
          dimid_yi(0),
          varid_time(0),
          varid_lat(0),
          varid_lon(0),
          varid_press(0),
          varid_u(0),
          varid_v(0) {}
    int grpid;
    int dimid_time;
    int dimid_xi;
    int dimid_yi;
    int varid_time;
    int varid_lat;
    int varid_lon;
    int varid_press;
    int varid_u;
    int varid_v;
  };

  explicit NcFile(std::string filename);

  ~NcFile();

  int ncid() const;
  std::vector<NcFile::NcGroup> *groups();

  void initialize();

  static void ncCheck(int err);

 private:
  std::string m_filename;
  int m_ncid;
  std::vector<NcGroup> m_groups;
};

#endif  // METGET_SRC_NCFILE_H_
