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
#include "NcFile.h"

#include <stdexcept>
#include <utility>

#include "netcdf.h"

NcFile::NcFile(std::string filename)
    : m_filename(std::move(filename)), m_ncid(0) {}

NcFile::~NcFile() {
  if (m_ncid != 0) {
    nc_close(m_ncid);
  }
}

void NcFile::ncCheck(const int err) {
  if (err != NC_NOERR) {
    throw std::runtime_error("Error from netCDF: " +
                             std::string(nc_strerror(err)));
  }
}

int NcFile::ncid() const { return m_ncid; }

std::vector<NcFile::NcGroup>* NcFile::groups() { return &m_groups; }

void NcFile::initialize() {
  ncCheck(nc_create(m_filename.c_str(), NC_NETCDF4, &m_ncid));
}
