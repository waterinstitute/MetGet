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
#include "OwiNetcdf.h"

#include <cmath>
#include <stdexcept>
#include <utility>

#include "netcdf.h"

OwiNetcdf::OwiNetcdf(std::string filename)
    : m_filename(std::move(filename)), m_file(m_filename) {}

int OwiNetcdf::initialize() {
  m_file.initialize();
  return 0;
}

void OwiNetcdf::addGroup(const std::string &name, unsigned int ni,
                         unsigned int nj, unsigned int nt, bool isMovingGrid) {
  NcFile::NcGroup grp;
  NcFile::ncCheck(nc_def_grp(m_file.ncid(), name.c_str(), &grp.grpid));
  NcFile::ncCheck(nc_def_dim(grp.grpid, "time", nt, &grp.dimid_time));
  NcFile::ncCheck(nc_def_dim(grp.grpid, "xi", ni, &grp.dimid_xi));
  NcFile::ncCheck(nc_def_dim(grp.grpid, "yi", nj, &grp.dimid_yi));

  NcFile::ncCheck(nc_def_var(grp.grpid, "time", NC_INT64, 1, &grp.dimid_time,
                             &grp.varid_time));

  int dim2d[] = {grp.dimid_yi, grp.dimid_xi};
  int dim3d[] = {grp.dimid_time, grp.dimid_yi, grp.dimid_xi};

  if (isMovingGrid) {
    NcFile::ncCheck(
        nc_def_var(grp.grpid, "lon", NC_FLOAT, 3, dim3d, &grp.varid_lon));
    NcFile::ncCheck(
        nc_def_var(grp.grpid, "lat", NC_FLOAT, 3, dim3d, &grp.varid_lat));
  } else {
    NcFile::ncCheck(
        nc_def_var(grp.grpid, "lon", NC_FLOAT, 2, dim2d, &grp.varid_lon));
    NcFile::ncCheck(
        nc_def_var(grp.grpid, "lat", NC_FLOAT, 2, dim2d, &grp.varid_lat));
  }

  NcFile::ncCheck(
      nc_def_var(grp.grpid, "U10", NC_FLOAT, 3, dim3d, &grp.varid_u));
  NcFile::ncCheck(
      nc_def_var(grp.grpid, "V10", NC_FLOAT, 3, dim3d, &grp.varid_v));
  NcFile::ncCheck(
      nc_def_var(grp.grpid, "PSFC", NC_FLOAT, 3, dim3d, &grp.varid_press));

  constexpr float nan = NAN;
  NcFile::ncCheck(nc_def_var_fill(grp.grpid, grp.varid_lat, 0, &nan));
  NcFile::ncCheck(nc_def_var_fill(grp.grpid, grp.varid_lon, 0, &nan));
  NcFile::ncCheck(nc_def_var_fill(grp.grpid, grp.varid_u, 0, &nan));
  NcFile::ncCheck(nc_def_var_fill(grp.grpid, grp.varid_v, 0, &nan));
  NcFile::ncCheck(nc_def_var_fill(grp.grpid, grp.varid_press, 0, &nan));

  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_lat, "units", NC_CHAR, 13,
                             "degrees_north"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_lat, "standard_name", NC_CHAR,
                             8, "latitude"));
  NcFile::ncCheck(
      nc_put_att(grp.grpid, grp.varid_lat, "axis", NC_CHAR, 1, "Y"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_lat, "coordinates", NC_CHAR,
                             12, "time lat lon"));

  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_lon, "units", NC_CHAR, 12,
                             "degrees_east"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_lon, "standard_name", NC_CHAR,
                             9, "longitude"));
  NcFile::ncCheck(
      nc_put_att(grp.grpid, grp.varid_lon, "axis", NC_CHAR, 1, "X"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_lon, "coordinates", NC_CHAR,
                             12, "time lat lon"));

  NcFile::ncCheck(
      nc_put_att(grp.grpid, grp.varid_u, "units", NC_CHAR, 5, "m s-1"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_u, "coordinates", NC_CHAR, 12,
                             "time lat lon"));

  NcFile::ncCheck(
      nc_put_att(grp.grpid, grp.varid_v, "units", NC_CHAR, 5, "m s-1"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_v, "coordinates", NC_CHAR, 12,
                             "time lat lon"));

  NcFile::ncCheck(
      nc_put_att(grp.grpid, grp.varid_press, "units", NC_CHAR, 2, "mb"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_press, "coordinates", NC_CHAR,
                             12, "time lat lon"));

  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_time, "units", NC_CHAR, 34,
                             "minutes since 1990-01-01T01:00:00"));
  NcFile::ncCheck(nc_put_att(grp.grpid, grp.varid_time, "calendar", NC_CHAR, 19,
                             "proleptic_gregorian"));

  NcFile::ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_time, 1, 1, 2));
  NcFile::ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_lat, 1, 1, 2));
  NcFile::ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_lon, 1, 1, 2));
  NcFile::ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_u, 1, 1, 2));
  NcFile::ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_v, 1, 1, 2));
  NcFile::ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_press, 1, 1, 2));

  m_file.groups()->push_back(grp);
  int rank = m_file.groups()->size();
  NcFile::ncCheck(
      nc_put_att_int(m_file.ncid(), NC_GLOBAL, "rank", NC_INT, 1, &rank));
}
void OwiNetcdf::writeToFile(const std::string &filename) {}
