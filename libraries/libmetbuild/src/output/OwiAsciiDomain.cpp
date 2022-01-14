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
#include "boost/format.hpp"

using namespace MetBuild;

OwiAsciiDomain::OwiAsciiDomain(const MetBuild::Grid *grid,
                               const Date &startDate, const Date &endDate,
                               const unsigned int time_step,
                               const std::string &pressureFile,
                               const std::string &windFile)
    : OutputDomain(grid, startDate, endDate, time_step),
      m_previousDate(startDate - time_step),
      m_ofstream_pressure(std::make_unique<std::ofstream>(pressureFile)),
      m_ofstream_wind(std::make_unique<std::ofstream>(windFile)),
      m_pressureFile(pressureFile),
      m_windFile(windFile) {
  assert(startDate < endDate);
}

OwiAsciiDomain::~OwiAsciiDomain() {
  if (m_ofstream_pressure->is_open()) {
    m_ofstream_pressure->close();
  }
  if (m_ofstream_wind->is_open()) {
    m_ofstream_wind->is_open();
  }
}

void OwiAsciiDomain::open() {
  if (!m_ofstream_pressure->is_open()) {
    m_ofstream_pressure->open(m_pressureFile);
  }
  if (!m_ofstream_wind->is_open()) {
    m_ofstream_wind->open(m_windFile);
  }
  this->write_header();
  this->set_open(true);
}

void OwiAsciiDomain::close() {
  if (!m_ofstream_pressure->is_open()) {
    m_ofstream_pressure->close();
  }
  if (!m_ofstream_wind->is_open()) {
    m_ofstream_wind->is_open();
  }
  this->set_open(false);
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

  *(m_ofstream_pressure) << generateRecordHeader(date, this->grid());
  *(m_ofstream_wind) << generateRecordHeader(date, this->grid());

  OwiAsciiDomain::write_record(m_ofstream_pressure.get(), data[2]);
  OwiAsciiDomain::write_record(m_ofstream_wind.get(), data[0]);
  OwiAsciiDomain::write_record(m_ofstream_wind.get(), data[1]);

  m_previousDate = date;

  return 0;
}

void OwiAsciiDomain::write_header() {
  auto header = generateHeaderLine(this->startDate(), this->endDate());
  *(m_ofstream_pressure) << header;
  *(m_ofstream_wind) << header;
}

std::string OwiAsciiDomain::generateHeaderLine(const Date &date1,
                                               const Date &date2) {
  return boost ::str(
      boost::format("Oceanweather WIN/PRE Format                         "
                    "   %4.4i%02d%02i%02i     %4.4i%02d%02i%02i\n") %
      date1.year() % date1.month() % date1.day() % date1.hour() % date2.year() %
      date2.month() % date2.day() % date2.hour());
}

std::string OwiAsciiDomain::formatHeaderCoordinates(const float value) {
  if (value <= -100.0) {
    return boost::str(boost::format("%8.3f") % value);
  } else if (value < 0.0 || value >= 100.0) {
    return boost::str(boost::format("%8.4f") % value);
  } else {
    return boost::str(boost::format("%8.5f") % value);
  }
}

std::string OwiAsciiDomain::generateRecordHeader(const Date &date,
                                                 const Grid *grid) {
  auto lon_string = formatHeaderCoordinates(grid->bottom_left().x());
  auto lat_string = formatHeaderCoordinates(grid->bottom_left().y());
  return boost::str(
      boost::format("iLat=%4diLong=%4dDX=%6.4fDY=%6.4fSWLat=%8sSWLon=%8sDT="
                    "%4.4i%02i%02i%02i%02i\n") %
      grid->nj() % grid->ni() % grid->dy() % grid->dx() % lat_string %
      lon_string % date.year() % date.month() % date.day() % date.hour() %
      date.minute());
}

void OwiAsciiDomain::write_record(
    std::ofstream *stream,
    const std::vector<std::vector<MetBuild::MeteorologicalDataType>> &value)
    const {
  constexpr size_t num_records_per_line = 8;
  size_t n = 0;
  for (size_t j = 0; j < this->grid()->nj(); ++j) {
    for (size_t i = 0; i < this->grid()->ni(); ++i) {
      *(stream) << boost::str(boost::format("%10.4f") % value[j][i]);
      n++;
      if (n == num_records_per_line) {
        *(stream) << "\n";
        n = 0;
      }
    }
  }
  if (n != num_records_per_line) *(stream) << "\n";
}
