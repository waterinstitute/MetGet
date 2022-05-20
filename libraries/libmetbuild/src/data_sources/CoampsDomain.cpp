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
#include "CoampsDomain.h"

#include "netcdf.h"

using namespace MetBuild;

CoampsDomain::CoampsDomain(std::string filename)
    : m_filename(std::move(filename)),
      m_ncid(std::make_unique<NetcdfFile>(m_filename)),
      m_dimid_lat(m_ncid->getDimid("lat")),
      m_dimid_lon(m_ncid->getDimid("lon")),
      m_nlon(m_ncid->getDimensionSize(m_dimid_lon)),
      m_nlat(m_ncid->getDimensionSize(m_dimid_lat)),
      m_varid_lat(m_ncid->getVarid("lat")),
      m_varid_lon(m_ncid->getVarid("lon")),
      m_varid_press(m_ncid->getVarid("slpres")),
      m_varid_uwind(m_ncid->getVarid("uuwind")),
      m_varid_vwind(m_ncid->getVarid("vvwind")),
      m_varid_rh(m_ncid->getVarid("relhum")),
      m_varid_temp(m_ncid->getVarid("airtmp")) {
  this->initialize();
}

void CoampsDomain::initialize() {
  size_t start[2] = {0, 0};
  size_t count[2] = {m_nlat, m_nlon};

  m_latitude.resize(m_nlat * m_nlon);
  m_longitude.resize(m_nlat * m_nlon);
  int ierr = nc_get_vara_double(m_ncid->ncid(), m_varid_lat, start, count,
                                m_latitude.data());
  ierr = nc_get_vara_double(m_ncid->ncid(), m_varid_lon, start, count,
                            m_longitude.data());
}