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
#include "DelftOutput.h"

#include <memory>
#include <utility>

#include "DelftDomain.h"

using namespace MetBuild;

DelftOutput::DelftOutput(const MetBuild::Date& date_start,
                         const MetBuild::Date& date_end, unsigned time_step,
                         std::string filename, bool use_compression)
    : OutputFile(date_start, date_end, time_step), 
      m_filename(std::move(filename)),
      m_use_compression(use_compression) {}

std::vector<std::string> DelftOutput::filenames() const {
  return m_domains[0]->filenames();
}

void DelftOutput::addDomain(const MetBuild::Grid& w,
                            const std::vector<std::string>& variables) {
  if (!m_domains.empty()) {
    metbuild_throw_exception(
        "Only one domain may be used for Delft formatted output");
  }
  this->m_domains.push_back(std::make_unique<DelftDomain>(
      &w, this->startDate(), this->endDate(), this->timeStep(), m_filename,
      variables, m_use_compression));
}

int DelftOutput::write(const MetBuild::Date& date, size_t domain_index,
                       const MetBuild::MeteorologicalData<1>& data) {
  return this->m_domains[0]->write(date, data);
}

int DelftOutput::write(const MetBuild::Date& date, size_t domain_index,
                       const MetBuild::MeteorologicalData<3>& data) {
  return this->m_domains[0]->write(date, data);
}
