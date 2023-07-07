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
#include "NetcdfFile.h"

#include "Logging.h"
#include "netcdf.h"

using namespace MetBuild;

NetcdfFile::NetcdfFile(const std::string& filename) : m_ncid(-1) {
  int ierr = nc_open(filename.c_str(), NC_NOWRITE, &m_ncid);
  if (ierr != NC_NOERR) {
    if (m_ncid != -1) {
      nc_close(m_ncid);
    }
    Logging::throwError("Error opening netCDF file: "+filename);
  }
}

NetcdfFile::~NetcdfFile() {
  if (m_ncid != -1) {
    int ierr = nc_close(m_ncid);
    if (ierr != NC_NOERR) {
      Logging::warning("Error during close of netCDF file.");
    }
  }
}

int NetcdfFile::ncid() const { return m_ncid; }

int NetcdfFile::getDimid(const std::string& name) const {
  int dimid = 0;
  int ierr = nc_inq_dimid(m_ncid, name.c_str(), &dimid);
  if (ierr != NC_NOERR) {
    Logging::throwError("Error reading netcdf dimension: " + name);
  }
  return dimid;
}

size_t NetcdfFile::getDimensionSize(int dimid) const {
  size_t size = 0;
  int ierr = nc_inq_dimlen(m_ncid, dimid, &size);
  if (ierr != NC_NOERR) {
    Logging::throwError("Error reading dimension size");
  }
  return size;
}

int NetcdfFile::getVarid(const std::string& name) const {
  int varid = 0;
  int ierr = nc_inq_varid(m_ncid, name.c_str(), &varid);
  if (ierr != NC_NOERR) {
    Logging::throwError("Error finding variable name:" + name);
  }
  return varid;
}
