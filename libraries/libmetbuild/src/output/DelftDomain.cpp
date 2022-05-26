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
#include "DelftDomain.h"

#include <utility>

#include "boost/algorithm/string.hpp"
#include "boost/iostreams/filter/gzip.hpp"
#include "boost/iostreams/filtering_streambuf.hpp"

#define FMT_HEADER_ONLY
#include "fmt/core.h"
#include "fmt/ostream.h"

using namespace MetBuild;

DelftDomain::DelftDomain(const MetBuild::Grid *grid,
                         const MetBuild::Date &startDate,
                         const MetBuild::Date &endDate, unsigned int time_step,
                         std::string filename,
                         std::vector<std::string> variables,
                         bool use_compression)
    : OutputDomain(grid, startDate, endDate, time_step),
      m_variables(std::move(variables)),
      m_baseFilename(std::move(filename)),
      m_use_compression(use_compression),
      m_default_compression_level(2) {
  this->_open();
}

DelftDomain::~DelftDomain() { this->_close(); }

void DelftDomain::open() { this->_open(); }

void DelftDomain::close() { this->_close(); }

void DelftDomain::_open() {
  this->m_filenames.reserve(m_variables.size());
  this->m_ofstreams.reserve(m_variables.size());
  const auto grid_unit = this->guessGridUnits();

  for (const auto &v : m_variables) {
    std::string filename, variableName, units;
    double multiplier;
    std::tie(filename, variableName, units, multiplier) =
        this->variableToFields(v);
    this->m_filenames.push_back(filename);

    if (m_use_compression) {
      this->m_ofstreams.emplace_back(
          this->m_filenames.back(), std::ios_base::out | std::ios_base::binary);
      this->m_compressedio_buffer.push_back(
          std::make_unique<boost::iostreams::filtering_streambuf<
              boost::iostreams::output>>());
      this->m_compressedio_buffer.back().get()->push(
          boost::iostreams::gzip_compressor(
              boost::iostreams::gzip_params(m_default_compression_level)));
      this->m_compressedio_buffer.back().get()->push(m_ofstreams.back());
      this->m_ostreams.push_back(
          std::make_unique<std::ostream>(m_compressedio_buffer.back().get()));
      this->writeHeader(this->m_ostreams.back().get(), variableName, units,
                        grid_unit);
    } else {
      this->m_ofstreams.emplace_back(this->m_filenames.back());
      this->writeHeader(&m_ofstreams.back(), variableName, units, grid_unit);
    }
  }
}

void DelftDomain::_close() {
  if (m_use_compression) {
    for (auto &b : m_compressedio_buffer) {
      b.reset(nullptr);
    }
  }
  for (auto &s : m_ofstreams) {
    s.close();
  }
}

int DelftDomain::write(
    const MetBuild::Date &date,
    const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
        &data) {
  std::string filename, variableName, units;
  double multiplier;
  std::tie(filename, variableName, units, multiplier) =
      this->variableToFields(m_variables[0]);
  if (m_use_compression) {
    return this->writeField(this->m_ostreams[0].get(), date, data[0]);
  } else {
    return this->writeField(&m_ofstreams[0], date, data[0]);
  }
}

int DelftDomain::write(
    const MetBuild::Date &date,
    const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
        &data) {
  int return_val = 0;
  for (size_t i = 0; i < 3; ++i) {
    std::string filename, variableName, units;
    double multiplier;
    std::tie(filename, variableName, units, multiplier) =
        this->variableToFields(m_variables[i]);
    if (m_use_compression) {
      return_val += this->writeField(this->m_ostreams[i].get(), date, data[i],
                                     multiplier);
    } else {
      return_val +=
          this->writeField(&m_ofstreams[i], date, data[i], multiplier);
    }
  }
  return return_val;
}

std::tuple<std::string, std::string, std::string, double>
DelftDomain::variableToFields(const std::string &variable) {
  auto v2 = boost::to_lower_copy(variable);
  if (variable == "wind_u") {
    return {this->m_baseFilename + ".amu", "x_wind", "m s-1", 1.0};
  } else if (variable == "wind_v") {
    return {this->m_baseFilename + ".amv", "y_wind", "m s-1", 1.0};
  } else if (variable == "mslp") {
    return {this->m_baseFilename + ".amp", "air_pressure", "Pa", 100.0};
  } else if (variable == "temperature") {
    return {this->m_baseFilename + ".amt", "temperature", "k", 1.0};
  } else if (variable == "humidity") {
    return {this->m_baseFilename + ".amh", "relative_humidity", "%", 1.0};
  } else if (variable == "ice") {
    return {this->m_baseFilename + ".ami", "ice_concentration", "%", 1.0};
  } else if (variable == "rain") {
    return {this->m_baseFilename + ".amr", "precipitation", "mm s-1", 1.0};
  } else {
    metbuild_throw_exception("Invalid variable " + variable + " specified.");
    return {};
  }
}

void DelftDomain::writeHeader(std::ostream *stream, const std::string &variable,
                              const std::string &units,
                              const std::string &grid_unit) {
  fmt::print(*(stream),
             "### START OF HEADER\n"
             "### This file generated by MetGet\n"
             "### File generated: {:s}\n"
             "FileVersion      = 1.03\n"
             "filetype         = meteo_on_equidistant_grid\n"
             "NODATA_value     = {:0.1f}\n"
             "n_cols           = {:d}\n"
             "n_rows           = {:d}\n"
             "grid_unit        = {:s}\n"
             "x_llcorner       = {:0.6f}\n"
             "y_llcorner       = {:0.6f}\n"
             "dx               = {:0.4f}\n"
             "dy               = {:0.4f}\n"
             "n_quantity       = 1\n"
             "quantity_1       = {:s}\n"
             "unit_1           = {:s}\n"
             "### END OF HEADER\n",
             Date::now().toString(), -999.0, this->grid()->ni(),
             this->grid()->nj(), grid_unit, this->grid()->bottom_left().x(),
             this->grid()->bottom_left().y(), this->grid()->dx(),
             this->grid()->dy(), variable, units);
}

template <typename T>
int DelftDomain::writeField(std::ostream *stream, const MetBuild::Date &date,
                            const std::vector<std::vector<T>> &data,
                            const double multiplier) {
  double hours =
      static_cast<double>(date.toSeconds() - this->startDate().toSeconds()) /
      3600.0;

  fmt::print(*(stream), "TIME = {:0.6f} hours since {:s} +00:00\n", hours,
             this->startDate().toString());

  for (const auto &r : data) {
    for (const auto &c : r) {
      fmt::print(*(stream), "{:0.6f} ", c * multiplier);
    }
    *(stream) << "\n";
  }
  return 0;
}
