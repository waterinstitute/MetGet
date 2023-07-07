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
#include "OwiAscii.h"

#include <cassert>

using namespace MetBuild;

OwiAscii::OwiAscii(const Date& startDate, const Date& endDate,
                   const unsigned time_step, const bool use_compression)
    : OutputFile(startDate, endDate, time_step),
      m_use_compression(use_compression) {}

void OwiAscii::addDomain(const Grid& w,
                         const std::vector<std::string>& filenames) {
  if (filenames.size() == 1) {
    m_domains.push_back(std::make_unique<OwiAsciiDomain>(
        &w, this->startDate(), this->endDate(), this->timeStep(), filenames[0],
        m_use_compression));
  } else if (filenames.size() == 2) {
    m_domains.push_back(std::make_unique<OwiAsciiDomain>(
        &w, this->startDate(), this->endDate(), this->timeStep(), filenames[0],
        filenames[1], m_use_compression));
  } else {
    metbuild_throw_exception("Must provide two filenames for OwiAscii format");
  }
}

int OwiAscii::write(const Date& date, const size_t domain_index,
                    const MeteorologicalData<1, MeteorologicalDataType>& data) {
  assert(domain_index < m_domains.size());
  return m_domains[domain_index]->write(date, data);
}

int OwiAscii::write(const Date& date, const size_t domain_index,
                    const MeteorologicalData<3, MeteorologicalDataType>& data) {
  assert(domain_index < m_domains.size());
  return m_domains[domain_index]->write(date, data);
}

void OwiAscii::close_domain(size_t domain) {
  assert(domain < m_domains.size());
  this->m_domains[domain]->close();
}
