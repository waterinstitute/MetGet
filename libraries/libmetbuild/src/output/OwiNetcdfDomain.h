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
#ifndef METGET_SRC_OUTPUT_OWINETCDFDOMAIN_H_
#define METGET_SRC_OUTPUT_OWINETCDFDOMAIN_H_

#include "Date.h"
#include "Grid.h"
#include "MeteorologicalData.h"
#include "OutputDomain.h"
#include "OwiNcFile.h"

namespace MetBuild {

class OwiNetcdfDomain : public OutputDomain {
 public:
  OwiNetcdfDomain(const MetBuild::Grid *grid, const MetBuild::Date &startDate,
                  const MetBuild::Date &endDate, unsigned time_step,
                  std::string groupName, MetBuild::OwiNcFile *netcdf);

  ~OwiNetcdfDomain() override = default;

  void open() override { this->m_ncFile->addGroup(m_groupName, this->grid()); }
  void close() override {}

  int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
          &data) override;

 private:
  MetBuild::OwiNcFile *m_ncFile;
  unsigned m_group;
  size_t m_counter;
  const std::string m_groupName;
};
}  // namespace MetBuild
#endif  // METGET_SRC_OUTPUT_OWINETCDFDOMAIN_H_
