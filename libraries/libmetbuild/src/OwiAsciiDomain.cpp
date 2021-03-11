//
// Created by Zach Cobell on 1/23/21.
//

#include "OwiAsciiDomain.h"

#include <cassert>
#include <utility>

#include "Logging.h"
#include "boost/format.hpp"

using namespace MetBuild;

OwiAsciiDomain::OwiAsciiDomain(const MetBuild::WindGrid *grid,
                               const Date &startDate, const Date &endDate,
                               const unsigned int time_step,
                               std::string pressureFile, std::string windFile)
    : m_isOpen(false),
      m_windGrid(grid),
      m_startDate(startDate),
      m_endDate(endDate),
      m_previousDate(startDate - time_step),
      m_timestep(time_step),
      m_pressureFile(std::move(pressureFile)),
      m_windFile(std::move(windFile)),
      m_ofstream_pressure(std::make_unique<std::ofstream>(pressureFile)),
      m_ofstream_wind(std::make_unique<std::ofstream>(windFile)) {
  assert(startDate < endDate);
  this->open();
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
  m_isOpen = true;
}

void OwiAsciiDomain::close() {
  if (!m_ofstream_pressure->is_open()) {
    m_ofstream_pressure->close();
  }
  if (!m_ofstream_wind->is_open()) {
    m_ofstream_wind->is_open();
  }
  m_isOpen = false;
}

int OwiAsciiDomain::write(const Date &date, const std::vector<double> &pressure,
                          const std::vector<double> &wind_u,
                          const std::vector<double> &wind_v) {
  if (!m_isOpen) {
    metbuild_throw_exception("OWI Domain not open");
  }
  if (date != m_previousDate + m_timestep) {
    metbuild_throw_exception("Non-constant time spacing detected");
  }
  if (date > m_endDate) {
    metbuild_throw_exception("Attempt to write past file end date");
  }

  *(m_ofstream_pressure) << generateRecordHeader(date, m_windGrid);
  *(m_ofstream_wind) << generateRecordHeader(date, m_windGrid);

  OwiAsciiDomain::write_record(m_ofstream_pressure.get(), pressure);
  OwiAsciiDomain::write_record(m_ofstream_wind.get(), wind_u);
  OwiAsciiDomain::write_record(m_ofstream_wind.get(), wind_v);

  m_previousDate = date;

  return 0;
}

void OwiAsciiDomain::write_header() {
  auto header = generateHeaderLine(m_startDate, m_endDate);
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

std::string OwiAsciiDomain::generateRecordHeader(const Date &date,
                                                 const WindGrid *grid) {
  return boost::str(
      boost::format("iLat=%4diLong=%4dDX=%6.4fDY=%6.4fSWLat=%8.5fSWLon=%8.4fDT="
                    "%4.4i%02i%02i%02i%02i\n") %
      grid->ni() % grid->nj() % grid->dx() % grid->dy() %
      grid->bottom_left().y() % grid->bottom_left().x() % date.year() %
      date.month() % date.day() % date.hour() % date.minute());
}

void OwiAsciiDomain::write_record(std::ofstream *stream,
                                  const std::vector<double> &value) {
  const size_t num_records_per_line = 8;
  size_t n = 0;
  for (const auto &v : value) {
    *(stream) << boost::str(boost::format(" %8.4f") % v);
    n++;
    if (n == num_records_per_line) {
      *(stream) << "\n";
      n = 0;
    }
  }
}