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

using namespace MetBuild;

OwiNetcdf::OwiNetcdf(const MetBuild::Date &date_start,
                     const MetBuild::Date &date_end, unsigned time_step,
                     std::string filename)
    : OutputFile(date_start, date_end, time_step),
      m_ncfile(std::move(filename)) {
  this->m_ncfile.initialize();
  this->m_filename = filename;
}

std::vector<std::string> OwiNetcdf::filenames() const {
  return {m_filename};
}

void OwiNetcdf::addDomain(const MetBuild::Grid &w,
                          const std::vector<std::string> &groupNames) {
  constexpr bool isMovingGrid = false;

  if (groupNames.empty()) {
    metbuild_throw_exception(
        "Must provide the name of the group for OwiNetcdf");
  }

  this->m_domains.push_back(std::make_unique<MetBuild::OwiNetcdfDomain>(
      &w, this->startDate(), this->endDate(), this->timeStep(), groupNames[0],
      &m_ncfile));
}

int OwiNetcdf::write(
    const Date &date, size_t domain_index,
    const MeteorologicalData<3, MetBuild::MeteorologicalDataType> &data) {
  return this->m_domains[domain_index]->write(date, data);
}
