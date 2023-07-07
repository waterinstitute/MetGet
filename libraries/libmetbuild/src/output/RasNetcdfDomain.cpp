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
#include "RasNetcdfDomain.h"

#include "Utilities.h"
#include "netcdf.h"

using namespace MetBuild;
using namespace Utilities;

RasNetcdfDomain::RasNetcdfDomain(const MetBuild::Grid *grid,
                                 const MetBuild::Date &startDate,
                                 const MetBuild::Date &endDate,
                                 unsigned int time_step, const int &ncid,
                                 std::vector<std::string> variables)
    : OutputDomain(grid, startDate, endDate, time_step),
      m_counter(0),
      m_ncid(ncid),
      m_dimid_x(0),
      m_dimid_y(0),
      m_dimid_time(0),
      m_varid_x(0),
      m_varid_y(0),
      m_varid_z(0),
      m_varid_time(0),
      m_varid_crs(0),
      m_variables(std::move(variables)) {
  this->initialize();
}

void RasNetcdfDomain::initialize() {
  auto nx = this->grid()->ni();
  auto ny = this->grid()->nj();

  const auto grid_unit = this->guessGridUnits();

  if (grid_unit == "deg") {
    ncCheck(nc_def_dim(m_ncid, "lon", nx, &m_dimid_x));
    ncCheck(nc_def_dim(m_ncid, "lat", ny, &m_dimid_y));
  } else {
    ncCheck(nc_def_dim(m_ncid, "x", nx, &m_dimid_x));
    ncCheck(nc_def_dim(m_ncid, "y", ny, &m_dimid_y));
  }
  ncCheck(nc_def_dim(m_ncid, "time", NC_UNLIMITED, &m_dimid_time));

  const int one[] = {1};
  const int twod[] = {m_dimid_y, m_dimid_x};
  const int threed[] = {m_dimid_time, m_dimid_y, m_dimid_x};
  const float float_fill = MeteorologicalData<1>::flag_value();
  // const double double_fill = MeteorologicalData<1>::flag_value();

  if (grid_unit == "deg") {
    // X
    ncCheck(nc_def_var(m_ncid, "lon", NC_DOUBLE, 1, &m_dimid_x, &m_varid_x));
    // ncCheck(nc_put_att_text(m_ncid, m_varid_x, "standard_name", 9,
    // "longitude"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_x, "long_name", 9, "Longitude"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_x, "units", 12, "degrees_east"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_x, "axis", 1, "X"));
    // ncCheck(nc_def_var_fill(m_ncid, m_varid_x, NC_FILL, &double_fill));
    ncCheck(nc_def_var_deflate(m_ncid, m_varid_x, 1, 1, 2));

    // Y
    ncCheck(nc_def_var(m_ncid, "lat", NC_DOUBLE, 1, &m_dimid_y, &m_varid_y));
    ////ncCheck(nc_put_att_text(m_ncid, m_varid_y, "standard_name", 8,
    ///"latitude"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_y, "long_name", 8, "Latitude"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_y, "units", 13, "degrees_north"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_y, "axis", 1, "Y"));
    // ncCheck(nc_def_var_fill(m_ncid, m_varid_y, NC_FILL, &double_fill));
    ncCheck(nc_def_var_deflate(m_ncid, m_varid_y, 1, 1, 2));
  } else {
    // X
    ncCheck(nc_def_var(m_ncid, "x", NC_DOUBLE, 1, &m_dimid_x, &m_varid_x));
    // ncCheck(nc_put_att_text(m_ncid, m_varid_x, "standard_name", 9, "x"));
    ncCheck(
        nc_put_att_text(m_ncid, m_varid_x, "long_name", 34, "x coordinate"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_x, "units", grid_unit.size(),
                            &grid_unit[0]));
    ncCheck(nc_put_att_text(m_ncid, m_varid_x, "axis", 1, "X"));
    // ncCheck(nc_def_var_fill(m_ncid, m_varid_x, NC_FILL, &double_fill));
    ncCheck(nc_def_var_deflate(m_ncid, m_varid_x, 1, 1, 2));

    // Y
    ncCheck(nc_def_var(m_ncid, "y", NC_DOUBLE, 1, &m_dimid_y, &m_varid_y));
    // ncCheck(nc_put_att_text(m_ncid, m_varid_y, "standard_name", 8, "y"));
    ncCheck(
        nc_put_att_text(m_ncid, m_varid_y, "long_name", 34, "y coordinate"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_y, "units", grid_unit.size(),
                            &grid_unit[0]));
    ncCheck(nc_put_att_text(m_ncid, m_varid_y, "axis", 1, "Y"));
    // ncCheck(nc_def_var_fill(m_ncid, m_varid_y, NC_FILL, &double_fill));
    ncCheck(nc_def_var_deflate(m_ncid, m_varid_y, 1, 1, 2));
  }

  // Z
  ncCheck(nc_def_var(m_ncid, "z", NC_DOUBLE, 2, twod, &m_varid_z));
  ncCheck(nc_put_att_text(m_ncid, m_varid_z, "units", 6, "meters"));
  ncCheck(nc_put_att_text(m_ncid, m_varid_z, "long_name", 27,
                          "height above mean sea level"));
  // ncCheck(nc_def_var_fill(m_ncid, m_varid_z, NC_FILL, &double_fill));
  ncCheck(nc_def_var_deflate(m_ncid, m_varid_z, 1, 1, 2));

  // TIME
  auto referenceTimeString =
      "minutes since " + this->startDate().toString("%F %T");
  ncCheck(
      nc_def_var(m_ncid, "time", NC_DOUBLE, 1, &m_dimid_time, &m_varid_time));
  // ncCheck(nc_put_att_text(m_ncid, m_varid_time, "standard_name", 4, "time"));
  ncCheck(nc_put_att_text(m_ncid, m_varid_time, "long_name", 4, "time"));
  ncCheck(nc_put_att_text(m_ncid, m_varid_time, "units",
                          referenceTimeString.size(), &referenceTimeString[0]));
  ncCheck(nc_put_att_text(m_ncid, m_varid_time, "axis", 1, "T"));
  // ncCheck(nc_def_var_fill(m_ncid, m_varid_time, NC_FILL, &double_fill));
  ncCheck(nc_def_var_deflate(m_ncid, m_varid_time, 1, 1, 2));

  // CRS
  if (grid_unit == "deg") {
    ncCheck(nc_def_var(m_ncid, "crs", NC_INT, 0, one, &m_varid_crs));
    ncCheck(nc_put_att_text(m_ncid, m_varid_crs, "long_name", 27,
                            "coordinate reference system"));
    ncCheck(nc_put_att_text(m_ncid, m_varid_crs, "grid_mapping_name", 18,
                            "latitude_longitude"));
    constexpr double zero = 0.0;
    ncCheck(nc_put_att_double(m_ncid, m_varid_crs,
                              "longitude_of_prime_meridian", NC_DOUBLE, 1,
                              &zero));
    constexpr double semi_major_axis = 6378137.0;
    ncCheck(nc_put_att_double(m_ncid, m_varid_crs, "semi_major_axis", NC_DOUBLE,
                              1, &semi_major_axis));
    constexpr double inverse_flattening = 298.257223563;
    ncCheck(nc_put_att_double(m_ncid, m_varid_crs, "inverse_flattening",
                              NC_DOUBLE, 1, &inverse_flattening));
    constexpr std::string_view wkt =
        "GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS "
        "84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY["
        "\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\","
        "\"8901\"]]"
        ",UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],"
        "AUTHORITY[\"EPSG\",\"4326\"]]";
    ncCheck(
        nc_put_att_text(m_ncid, m_varid_crs, "crs_wkt", wkt.size(), &wkt[0]));
    constexpr std::string_view proj4 =
        "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs";
    ncCheck(nc_put_att_text(m_ncid, m_varid_crs, "proj4_params", proj4.size(),
                            &proj4[0]));
    ncCheck(nc_put_att_text(m_ncid, m_varid_crs, "epsg_code", 9, "EPSG:4326"));
  }

  this->m_varids.reserve(m_variables.size());
  for (const auto &v : m_variables) {
    std::string standard_name;
    std::string long_name;
    std::string units;
    if (v == "wind_u") {
      standard_name = "eastward_wind";
      long_name = "e/w wind velocity";
      units = "m/s";
    } else if (v == "wind_v") {
      standard_name = "northward_wind";
      long_name = "n/s wind velocity";
      units = "m/s";
    } else if (v == "mslp") {
      standard_name = "air_pressure_at_sea_level";
      long_name = "air pressure at sea level";
      units = "mb";
    } else if (v == "rain") {
      standard_name = "rainfall_rate";
      long_name = "Total rainfall accumulation over 1 hour";
      units = "mm";
    } else if (v == "humidity") {
      standard_name = "relative_humidity";
      long_name = "relative humidity in air at ground level";
      units = "percent";
    } else if (v == "temperature") {
      standard_name = "air_temperature";
      long_name = "air temperature at ground level";
      units = "degC";
    }

    int varid = 0;
#ifdef METBUILD_USE_FLOAT
    ncCheck(nc_def_var(m_ncid, &v[0], NC_FLOAT, 3, threed, &varid));
    ncCheck(nc_def_var_fill(m_ncid, varid, NC_FILL, &float_fill));
#else
    ncCheck(nc_def_var(m_ncid, &v[0], NC_DOUBLE, 3, threed, &varid));
    ncCheck(nc_def_var_fill(m_ncid, varid, NC_FILL, &double_fill));
#endif
    // ncCheck(nc_put_att_text(m_ncid, varid, "standard_name",
    //                         standard_name.size(), &standard_name[0]));
    ncCheck(nc_put_att_text(m_ncid, varid, "long_name", long_name.size(),
                            &long_name[0]));
    ncCheck(nc_put_att_text(m_ncid, varid, "units", units.size(), &units[0]));
    ncCheck(nc_put_att_text(m_ncid, varid, "grid_mapping", 3, "crs"));
    ncCheck(nc_def_var_deflate(m_ncid, varid, 1, 1, 2));
    this->m_varids.push_back(varid);
  }

  ncCheck(nc_enddef(m_ncid));

  const auto x = this->grid()->xcolumn();
  const auto y = this->grid()->ycolumn();
  const size_t start[] = {0};

  ncCheck(nc_put_vara(m_ncid, m_varid_x, start, &nx, x.data()));
  ncCheck(nc_put_vara(m_ncid, m_varid_y, start, &ny, y.data()));
}

int RasNetcdfDomain::write(const MetBuild::Date &date,
                           const MetBuild::MeteorologicalData<1> &data) {
  const double minutes[] = {
      (static_cast<double>(date.toSeconds() - this->startDate().toSeconds())) /
      60.0};  // time offset in minutes
  const size_t start_array[] = {m_counter, 0, 0};
  const size_t count_array[] = {1, this->grid()->nj(), this->grid()->ni()};
  const size_t start_scalar[] = {m_counter};
  const size_t count_scalar[] = {1};

  ncCheck(nc_put_vara_double(m_ncid, m_varid_time, start_scalar, count_scalar,
                             minutes));

  const auto array = data.toVector(0);
#ifdef METBUILD_USE_FLOAT
  ncCheck(nc_put_vara_float(m_ncid, m_varids[0], start_array, count_array,
                            array.data()));
#else
  ncCheck(nc_put_vara_double(m_ncid, m_varids[0], start_array, count_array,
                             array.data()));
#endif

  m_counter++;
  return 0;
}

int RasNetcdfDomain::write(const MetBuild::Date &date,
                           const MetBuild::MeteorologicalData<3> &data) {
  const double minutes[] = {
      (static_cast<double>(date.toSeconds() - this->startDate().toSeconds())) /
      60.0};  // time offset in minutes
  const size_t start_array[] = {m_counter, 0, 0};
  const size_t count_array[] = {1, this->grid()->nj(), this->grid()->ni()};
  const size_t start_scalar[] = {m_counter};
  const size_t count_scalar[] = {1};

  ncCheck(nc_put_vara_double(m_ncid, m_varid_time, start_scalar, count_scalar,
                             minutes));

  for (size_t i = 0; i < m_varids.size(); ++i) {
    const auto array = data.toVector(i);
#ifdef METBUILD_USE_FLOAT
    ncCheck(nc_put_vara_float(m_ncid, m_varids[i], start_array, count_array,
                              array.data()));
#else
    ncCheck(nc_put_vara_double(m_ncid, m_varids[i], start_array, count_array,
                               array.data()));
#endif
  }

  m_counter++;
  return 0;
}
