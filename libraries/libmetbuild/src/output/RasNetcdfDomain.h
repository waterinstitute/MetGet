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
#ifndef METGET_SRC_OUTPUT_RASNETCDFDOMAIN_H_
#define METGET_SRC_OUTPUT_RASNETCDFDOMAIN_H_

#include "MeteorologicalData.h"
#include "OutputDomain.h"

namespace MetBuild {

class RasNetcdfDomain : public OutputDomain {
 public:
  RasNetcdfDomain(const MetBuild::Grid *grid, const MetBuild::Date &startDate,
                  const MetBuild::Date &endDate, unsigned time_step,
                  const int &ncid, std::vector<std::string> variables);

  ~RasNetcdfDomain() override = default;

  void open() override {}

  void close() override {}

  int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
          &data) override;

  int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
          &data) override;

 private:
  void initialize();

  size_t m_counter;
  const int m_ncid;

  int m_dimid_x;
  int m_dimid_y;
  int m_dimid_time;
  int m_varid_x;
  int m_varid_y;
  int m_varid_z;
  int m_varid_time;
  int m_varid_crs;

  const std::vector<std::string> m_variables;
  std::vector<int> m_varids;
  std::vector<int> m_dimids;
};

}  // namespace MetBuild
#endif  // METGET_SRC_OUTPUT_RASNETCDFDOMAIN_H_
