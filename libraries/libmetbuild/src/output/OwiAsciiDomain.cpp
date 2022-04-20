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
#include "OwiAsciiDomain.h"

#include <cassert>

#include "Logging.h"
#include "boost/iostreams/filter/gzip.hpp"

#define FMT_HEADER_ONLY
#include "fmt/core.h"
#include "fmt/ostream.h"

using namespace MetBuild;

OwiAsciiDomain::OwiAsciiDomain(const MetBuild::Grid *grid,
                               const Date &startDate, const Date &endDate,
                               const unsigned int time_step,
                               const std::string &pressureFile,
                               const std::string &windFile,
                               const bool use_compression)
    : OutputDomain(grid, startDate, endDate, time_step),
      m_previousDate(startDate - time_step),
      m_compressed_stream_pressure(&m_compressedio_pressure),
      m_compressed_stream_wind(&m_compressedio_wind),
      m_pressureFile(pressureFile),
      m_windFile(windFile),
      m_use_compression(use_compression),
      m_default_compression_level(2) {
  assert(startDate < endDate);
  this->m_filenames.push_back(pressureFile);
  this->m_filenames.push_back(windFile);
  this->_open();
}

OwiAsciiDomain::OwiAsciiDomain(const MetBuild::Grid *grid,
                               const Date &startDate, const Date &endDate,
                               const unsigned int time_step,
                               const std::string &outputFile,
                               const bool use_compression)
    : OutputDomain(grid, startDate, endDate, time_step),
      m_previousDate(startDate - time_step),
      m_compressed_stream_pressure(&m_compressedio_pressure),
      m_compressed_stream_wind(&m_compressedio_wind),
      m_pressureFile(outputFile),
      m_use_compression(use_compression),
      m_default_compression_level(2) {
  assert(startDate < endDate);
  this->m_filenames.push_back(outputFile);
  this->_open();
}

void OwiAsciiDomain::open() { this->_open(); }

OwiAsciiDomain::~OwiAsciiDomain() { this->_close(); }

void OwiAsciiDomain::_open() {
  if (m_use_compression) {
    if (!m_ofstream_pressure.is_open()) {
      m_ofstream_pressure.open(m_pressureFile,
                               std::ios_base::out | std::ios_base::binary);
      m_compressedio_pressure.push(boost::iostreams::gzip_compressor(
          boost::iostreams::gzip_params(m_default_compression_level)));
      m_compressedio_pressure.push(m_ofstream_pressure);
    }
    if (!m_windFile.empty()) {
      if (!m_ofstream_wind.is_open()) {
        m_ofstream_wind.open(m_windFile,
                             std::ios_base::out | std::ios_base::binary);
        m_compressedio_wind.push(boost::iostreams::gzip_compressor(
            boost::iostreams::gzip_params(m_default_compression_level)));
        m_compressedio_wind.push(m_ofstream_wind);
      }
    }
  } else {
    if (!m_ofstream_pressure.is_open()) {
      m_ofstream_pressure.open(m_pressureFile);
    }
    if (!m_windFile.empty()) {
      if (!m_ofstream_wind.is_open()) {
        m_ofstream_wind.open(m_windFile);
      }
    }
  }
  this->write_header();
  this->set_open(true);
}

void OwiAsciiDomain::close() { this->_close(); }

void OwiAsciiDomain::_close() {
  if (m_ofstream_pressure.is_open()) {
    if (m_use_compression) boost::iostreams::close(m_compressedio_pressure);
    m_ofstream_pressure.close();
  }
  if (m_ofstream_wind.is_open()) {
    if (m_use_compression) boost::iostreams::close(m_compressedio_wind);
    m_ofstream_wind.close();
  }
  this->set_open(false);
}

int OwiAsciiDomain::write(
    const Date &date,
    const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
        &data) {
  if (!this->is_open()) {
    metbuild_throw_exception("OWI Domain not open");
  }
  if (date != m_previousDate + this->timestep()) {
    metbuild_throw_exception("Non-constant time spacing detected");
  }
  if (date > this->endDate()) {
    metbuild_throw_exception("Attempt to write past file end date");
  }

  auto header = generateRecordHeader(date, this->grid());
  if (m_use_compression) {
    m_ofstream_pressure << header;
  } else {
    m_ofstream_pressure << header;
  }

  if (m_use_compression) {
    OwiAsciiDomain::write_record(&m_compressed_stream_pressure, data[0]);
  } else {
    OwiAsciiDomain::write_record(&m_ofstream_pressure, data[0]);
  }

  m_previousDate = date;

  return 0;
}

int OwiAsciiDomain::write(
    const Date &date,
    const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
        &data) {
  if (!this->is_open()) {
    metbuild_throw_exception("OWI Domain not open");
  }
  if (date != m_previousDate + this->timestep()) {
    metbuild_throw_exception("Non-constant time spacing detected");
  }
  if (date > this->endDate()) {
    metbuild_throw_exception("Attempt to write past file end date");
  }

  auto header = generateRecordHeader(date, this->grid());
  if (m_use_compression) {
    m_compressed_stream_pressure << header;
    m_compressed_stream_wind << header;
    OwiAsciiDomain::write_record(&m_compressed_stream_pressure, data[2]);
    OwiAsciiDomain::write_record(&m_compressed_stream_wind, data[0]);
    OwiAsciiDomain::write_record(&m_compressed_stream_wind, data[1]);
  } else {
    m_ofstream_pressure << header;
    m_ofstream_wind << header;
    OwiAsciiDomain::write_record(&m_ofstream_pressure, data[2]);
    OwiAsciiDomain::write_record(&m_ofstream_wind, data[0]);
    OwiAsciiDomain::write_record(&m_ofstream_wind, data[1]);
  }

  m_previousDate = date;

  return 0;
}

void OwiAsciiDomain::write_header() {
  auto header = generateHeaderLine(this->startDate(), this->endDate());
  if (m_use_compression) {
    m_compressed_stream_pressure << header;
    if (!m_windFile.empty()) {
      m_compressed_stream_wind << header;
    }
  } else {
    m_ofstream_pressure << header;
    if (!m_windFile.empty()) {
      m_ofstream_wind << header;
    }
  }
}

std::string OwiAsciiDomain::generateHeaderLine(const Date &date1,
                                               const Date &date2) {
  return fmt::format(
      "Oceanweather WIN/PRE Format                         "
      "   {:04d}{:02d}{:02d}{:02d}     {:04d}{:02d}{:02d}{:02d}\n",
      date1.year(), date1.month(), date1.day(), date1.hour(), date2.year(),
      date2.month(), date2.day(), date2.hour());
}

std::string OwiAsciiDomain::formatHeaderCoordinates(const float value) {
  if (value <= -100.0) {
    return fmt::format("{:8.3f}", value);
  } else if (value < 0.0 || value >= 100.0) {
    return fmt::format("{:8.4f}", value);
  } else {
    return fmt::format("{:8.5f}", value);
  }
}

std::string OwiAsciiDomain::generateRecordHeader(const Date &date,
                                                 const Grid *grid) {
  auto lon_string = formatHeaderCoordinates(grid->bottom_left().x());
  auto lat_string = formatHeaderCoordinates(grid->bottom_left().y());
  return fmt::format(
      "iLat={:4d}iLong={:4d}DX={:6.4f}DY={:6.4f}SWLat={:8s}SWLon={:8s}DT="
      "{:04d}{:02d}{:02d}{:02d}{:02d}\n",
      grid->nj(), grid->ni(), grid->dy(), grid->dx(), lat_string, lon_string,
      date.year(), date.month(), date.day(), date.hour(), date.minute());
}

void OwiAsciiDomain::write_record(
    std::ostream *stream,
    const std::vector<std::vector<MetBuild::MeteorologicalDataType>> &value)
    const {
  constexpr size_t num_records_per_line = 8;
  size_t n = 0;
  for (size_t j = 0; j < this->grid()->nj(); ++j) {
    for (size_t i = 0; i < this->grid()->ni(); ++i) {
      fmt::print(*(stream), "{:10.4f}", value[j][i]);
      n++;
      if (n == num_records_per_line) {
        *(stream) << "\n";
        n = 0;
      }
    }
  }
  *(stream) << "\n";
}
