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
#include "OwiNetcdfDomain.h"

#include <utility>

MetBuild::OwiNetcdfDomain::OwiNetcdfDomain(const MetBuild::Grid *grid,
                                           const MetBuild::Date &startDate,
                                           const MetBuild::Date &endDate,
                                           unsigned int time_step,
                                           std::string groupName,
                                           MetBuild::OwiNcFile *netcdf)
    : OutputDomain(grid, startDate, endDate, time_step),
      m_ncFile(netcdf),
      m_group(m_ncFile->groups()->size()),
      m_counter(0),
      m_groupName(std::move(groupName)) {
  m_ncFile->addGroup(m_groupName, this->grid());
}

int MetBuild::OwiNetcdfDomain::write(
    const MetBuild::Date &date,
    const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
        &data) {
  auto seconds =
      date.toSeconds() - MetBuild::Date(1990, 1, 1, 1, 0, 0).toSeconds();
#ifdef METBUILD_USE_FLOAT
  this->m_ncFile->write(m_group, m_counter, seconds, data.toVector(0),
                        data.toVector(1), data.toVector(2));
#else
  auto data2 = MetBuild::MeteorologicalData<3>::recast<3, double, float>(data);
  this->m_ncFile->write(m_group, m_counter, seconds, data2.toVector(0),
                        data2.toVector(1), data2.toVector(3));
#endif
  m_counter++;
  return 0;
}
