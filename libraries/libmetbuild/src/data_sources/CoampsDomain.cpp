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
#include "CoampsDomain.h"

#include <algorithm>
#include <cassert>

#include "Logging.h"
#include "Point.h"
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
      m_varid_lon(m_ncid->getVarid("lon")) {
  this->initialize();
}

void CoampsDomain::initialize() {
  size_t start[2] = {0, 0};
  size_t count[2] = {m_nlat, m_nlon};

  m_latitude.resize(this->size());
  m_longitude.resize(this->size());
  m_mask.resize(this->size());

  int ierr = nc_get_vara_double(m_ncid->ncid(), m_varid_lat, start, count,
                                m_latitude.data());
  if (ierr != NC_NOERR) {
    Logging::throwError("Could not read latitude values from COAMPS file");
  }

  ierr = nc_get_vara_double(m_ncid->ncid(), m_varid_lon, start, count,
                            m_longitude.data());
  if (ierr != NC_NOERR) {
    Logging::throwError("Could not read longitude files from COAMPS file");
  }

  for (auto& v : m_longitude) {
    v = CoampsDomain::normalize_longitude(v);
  }
  this->findCorners();
}

/**
 * Adjustment for COAMPS coordinates which can be in excess of 360 and also do
 * not have the -180/180 orientation we typically use in adcirc
 * @param longitude coordinate to normalize
 * @return normalized coordinate
 */
double CoampsDomain::normalize_longitude(const double longitude) {
  double lon = std::fmod(longitude, 360.0);
  return lon > 180.0 ? lon -= 360.0 : lon;
}

void CoampsDomain::findCorners() {
  const double xtl = m_longitude[m_nlon * (m_nlat - 1)];
  const double xtr = m_longitude[m_nlon * m_nlat - 1];
  const double xll = m_longitude[0];
  const double xlr = m_longitude[m_nlon - 1];

  const double ytl = m_latitude[m_nlon * (m_nlat - 1)];
  const double ytr = m_latitude[m_nlon * m_nlat - 1];
  const double yll = m_latitude[0];
  const double ylr = m_latitude[m_nlon - 1];

  m_corners = {Point(xll, yll), Point(xlr, ylr), Point(xtr, ytr),
               Point(xtl, ytl)};
  m_point_ll = Point(xll, yll);
  m_point_ur = Point(xtr, ytr);
}

NetcdfFile* CoampsDomain::ncid() { return this->m_ncid.get(); }

std::array<Point, 4> CoampsDomain::corners() const { return m_corners; }

size_t CoampsDomain::nlat() const { return m_nlat; }

size_t CoampsDomain::nlon() const { return m_nlon; }

size_t CoampsDomain::size() const { return m_nlon * m_nlat; }

double CoampsDomain::longitude(size_t index) const {
  assert(index < m_longitude.size());
  return m_longitude[index];
}

double CoampsDomain::latitude(size_t index) const {
  assert(index < m_latitude.size());
  return m_latitude[index];
}

bool CoampsDomain::masked(size_t index) const {
  assert(index < m_mask.size());
  return m_mask[index];
}

void CoampsDomain::setMask(size_t index, bool value) {
  assert(index < m_mask.size());
  if (m_mask[index] != value) {
    if (value) {
      m_mask_count++;
    } else {
      m_mask_count--;
    }
    m_mask[index] = value;
  }
}

size_t CoampsDomain::n_masked_points() const { return m_mask_count; }

std::array<std::vector<double>, 2> CoampsDomain::getUnmaskedCoordinates()
    const {
  std::vector<double> lon;
  lon.reserve(this->size());
  std::vector<double> lat;
  lat.reserve(this->size());

  for (size_t i = 0; i < this->size(); ++i) {
    if (!m_mask[i]) {
      lon.push_back(m_longitude[i]);
      lat.push_back(m_latitude[i]);
    }
  }
  return {lon, lat};
}

std::vector<double> CoampsDomain::get(const std::string& variable) const {
  const auto variable_id = m_ncid->getVarid(variable);
  std::vector<float> var(this->size());
  std::vector<double> var_out;
  var_out.reserve(this->size());

  const size_t start[2] = {0, 0};
  const size_t count[2] = {m_nlat, m_nlon};
  int ierr =
      nc_get_vara_float(m_ncid->ncid(), variable_id, start, count, var.data());
  if (ierr != NC_NOERR) {
    Logging::throwError("Could not read variable " + variable +
                        " from COAMPS file");
  }

  for (size_t i = 0; i < this->size(); ++i) {
    if (!m_mask[i]) {
      var_out.push_back(static_cast<double>(var[i]));
    }
  }
  return var_out;
}

const Point& CoampsDomain::point_ll() const { return m_point_ll; }

const Point& CoampsDomain::point_ur() const { return m_point_ur; }

std::vector<Point> CoampsDomain::get_bounding_region() const {
  std::vector<Point> region;

  // Bottom left --> Bottom right
  for (size_t i = 0; i < m_nlon; ++i) {
    region.emplace_back(m_longitude[i], m_latitude[i]);
  }
  // Bottom right --> Top right
  for (size_t i = 1; i < m_nlat; ++i) {
    region.emplace_back(m_longitude[i * m_nlon - 1],
                        m_latitude[i * m_nlon - 1]);
  }

  // Top Right --> Top Left
  for (size_t i = 0; i < m_nlon; ++i) {
    region.emplace_back(m_longitude[m_nlat * m_nlon - 1 - i],
                        m_latitude[m_nlat * m_nlon - 1 - i]);
  }

  // Top left --> Bottom Left
  for (long i = static_cast<long>(m_nlat) - 1; i > 0; --i) {
    region.emplace_back(m_longitude[i * m_nlon], m_latitude[i * m_nlon]);
  }

  return region;
}
