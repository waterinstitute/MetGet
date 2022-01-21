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
#include "OwiNcFile.h"

#include <cmath>
#include <stdexcept>
#include <utility>

#include "Date.h"
#include "Utilities.h"
#include "netcdf.h"

using namespace MetBuild;
using namespace Utilities;

OwiNcFile::OwiNcFile(std::string filename)
    : m_filename(std::move(filename)), m_ncid(0) {}

OwiNcFile::~OwiNcFile() {
  if (m_ncid != 0) {
    std::string group_order;
    for(auto i=0;i<m_groups.size();++i){
      if(i+1 < m_groups.size()){
        group_order += m_groups[i].name + " ";
      } else {
        group_order += m_groups[i].name;
      }
    }
    const size_t len = group_order.size();
    ncCheck(nc_put_att(m_ncid, NC_GLOBAL, "group_order", NC_CHAR, len, &group_order[0]));
    nc_close(m_ncid);
  }
}

int OwiNcFile::ncid() const { return m_ncid; }

std::vector<OwiNcFile::NcGroup>* OwiNcFile::groups() { return &m_groups; }

void OwiNcFile::initialize() {
  ncCheck(nc_create(m_filename.c_str(), NC_NETCDF4, &m_ncid));
  constexpr std::string_view metget = "metget";
  constexpr std::string_view conventions = "CF-1.6 OWI-NWS13";
  const auto now = Date::now().toString();
  ncCheck(nc_put_att(m_ncid, NC_GLOBAL, "institution", NC_CHAR, metget.size(), &metget[0]));
  ncCheck(nc_put_att(m_ncid, NC_GLOBAL, "conventions", NC_CHAR, conventions.size(), &conventions[0]));
  ncCheck(nc_put_att(m_ncid, NC_GLOBAL, "creation_date", NC_CHAR, now.size(), &now[0]));
  ncCheck(nc_enddef(m_ncid));
}

int OwiNcFile::addGroup(const std::string& groupName,
                        const MetBuild::Grid* grid, const bool isMovingGrid) {

  ncCheck(nc_redef(this->ncid()));

  OwiNcFile::NcGroup grp;
  grp.name = groupName;
  ncCheck(nc_def_grp(this->ncid(), groupName.c_str(), &grp.grpid));
  ncCheck(nc_def_dim(grp.grpid, "time", 0, &grp.dimid_time));
  ncCheck(nc_def_dim(grp.grpid, "xi", grid->ni(), &grp.dimid_xi));
  ncCheck(nc_def_dim(grp.grpid, "yi", grid->nj(), &grp.dimid_yi));
  grp.ni = grid->ni();
  grp.nj = grid->nj();

  ncCheck(nc_def_var(grp.grpid, "time", NC_INT64, 1, &grp.dimid_time,
                     &grp.varid_time));

  int dim2d[] = {grp.dimid_yi, grp.dimid_xi};
  int dim3d[] = {grp.dimid_time, grp.dimid_yi, grp.dimid_xi};

  if (isMovingGrid) {
    ncCheck(nc_def_var(grp.grpid, "lon", NC_FLOAT, 3, dim3d, &grp.varid_lon));
    ncCheck(nc_def_var(grp.grpid, "lat", NC_FLOAT, 3, dim3d, &grp.varid_lat));
  } else {
    ncCheck(nc_def_var(grp.grpid, "lon", NC_FLOAT, 2, dim2d, &grp.varid_lon));
    ncCheck(nc_def_var(grp.grpid, "lat", NC_FLOAT, 2, dim2d, &grp.varid_lat));
  }

  ncCheck(nc_def_var(grp.grpid, "U10", NC_FLOAT, 3, dim3d, &grp.varid_u));
  ncCheck(nc_def_var(grp.grpid, "V10", NC_FLOAT, 3, dim3d, &grp.varid_v));
  ncCheck(nc_def_var(grp.grpid, "PSFC", NC_FLOAT, 3, dim3d, &grp.varid_press));

  constexpr float nan = NAN;
  ncCheck(nc_def_var_fill(grp.grpid, grp.varid_lat, 0, &nan));
  ncCheck(nc_def_var_fill(grp.grpid, grp.varid_lon, 0, &nan));
  ncCheck(nc_def_var_fill(grp.grpid, grp.varid_u, 0, &nan));
  ncCheck(nc_def_var_fill(grp.grpid, grp.varid_v, 0, &nan));
  ncCheck(nc_def_var_fill(grp.grpid, grp.varid_press, 0, &nan));

  ncCheck(nc_put_att(grp.grpid, grp.varid_lat, "units", NC_CHAR, 13,
                     "degrees_north"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_lat, "standard_name", NC_CHAR, 8,
                     "latitude"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_lat, "axis", NC_CHAR, 1, "Y"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_lat, "coordinates", NC_CHAR, 12,
                     "time lat lon"));

  ncCheck(nc_put_att(grp.grpid, grp.varid_lon, "units", NC_CHAR, 12,
                     "degrees_east"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_lon, "standard_name", NC_CHAR, 9,
                     "longitude"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_lon, "axis", NC_CHAR, 1, "X"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_lon, "coordinates", NC_CHAR, 12,
                     "time lat lon"));

  ncCheck(nc_put_att(grp.grpid, grp.varid_u, "units", NC_CHAR, 5, "m s-1"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_u, "coordinates", NC_CHAR, 12,
                     "time lat lon"));

  ncCheck(nc_put_att(grp.grpid, grp.varid_v, "units", NC_CHAR, 5, "m s-1"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_v, "coordinates", NC_CHAR, 12,
                     "time lat lon"));

  ncCheck(nc_put_att(grp.grpid, grp.varid_press, "units", NC_CHAR, 2, "mb"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_press, "coordinates", NC_CHAR, 12,
                     "time lat lon"));

  ncCheck(nc_put_att(grp.grpid, grp.varid_time, "units", NC_CHAR, 34,
                     "minutes since 1990-01-01T01:00:00"));
  ncCheck(nc_put_att(grp.grpid, grp.varid_time, "calendar", NC_CHAR, 19,
                     "proleptic_gregorian"));

  ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_time, 1, 1, 2));
  ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_lat, 1, 1, 2));
  ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_lon, 1, 1, 2));
  ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_u, 1, 1, 2));
  ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_v, 1, 1, 2));
  ncCheck(nc_def_var_deflate(grp.grpid, grp.varid_press, 1, 1, 2));

  this->groups()->push_back(grp);
  int rank = static_cast<int>(this->groups()->size());
  ncCheck(nc_put_att_int(grp.grpid, NC_GLOBAL, "rank", NC_INT, 1, &rank));
  ncCheck(nc_enddef(this->ncid()));

  if (!isMovingGrid) {
    const auto x = grid->x();
    const auto y = grid->y();
    const size_t start[] = {0,0};
    const size_t count[] = {grid->nj(), grid->ni()};
    ncCheck(nc_put_vara_double(grp.grpid, grp.varid_lat, start, count, y.data()));
    ncCheck(nc_put_vara_double(grp.grpid, grp.varid_lon, start, count, x.data()));
  }

  return 0;
}

int OwiNcFile::write(unsigned group_index, size_t time_index, size_t time,
                     const std::vector<float>& u, const std::vector<float>& v,
                     const std::vector<float>& p) {
  const size_t start[] = {time_index, 0, 0};
  const size_t count[] = {1, m_groups[group_index].nj,
                          m_groups[group_index].ni};
  constexpr size_t one = 1;
  const auto time_long = static_cast<long long>(time);

  ncCheck(nc_put_vara_longlong(m_groups[group_index].grpid, m_groups[group_index].varid_time,
                               &time_index, &one, &time_long));
  ncCheck(nc_put_vara_float(m_groups[group_index].grpid, m_groups[group_index].varid_u, start,
                            count, u.data()));
  ncCheck(nc_put_vara_float(m_groups[group_index].grpid, m_groups[group_index].varid_v, start,
                            count, v.data()));
  ncCheck(nc_put_vara_float(m_groups[group_index].grpid, m_groups[group_index].varid_press,
                            start, count, p.data()));

  return 0;
}

int OwiNcFile::write(unsigned group_index, size_t time_index, size_t time,
                     const std::vector<float>& x, const std::vector<float>& y,
                     const std::vector<float>& u, const std::vector<float>& v,
                     const std::vector<float>& p) {
  const size_t start[] = {time_index, 0, 0};
  const size_t count[] = {1, m_groups[group_index].ni,
                          m_groups[group_index].nj};

  ncCheck(nc_put_vara_float(this->ncid(), m_groups[group_index].varid_lon,
                            start, count, x.data()));
  ncCheck(nc_put_vara_float(this->ncid(), m_groups[group_index].varid_lat,
                            start, count, y.data()));
  return this->write(group_index, time_index, time, u, v, p);
}
