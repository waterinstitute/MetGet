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
#ifndef METGET_LIBRARY_OWIASCIIDOMAIN_H_
#define METGET_LIBRARY_OWIASCIIDOMAIN_H_

#include <fstream>
#include <memory>
#include <string>
#include <vector>

#include "Date.h"
#include "Grid.h"
#include "MeteorologicalData.h"
#include "OutputDomain.h"

namespace MetBuild {

class OwiAsciiDomain : public OutputDomain {
 public:
  OwiAsciiDomain(const MetBuild::Grid *grid, const MetBuild::Date &startDate,
                 const MetBuild::Date &endDate, unsigned time_step,
                 const std::string &pressureFile, const std::string &windFile);
  
  OwiAsciiDomain(const MetBuild::Grid *grid, const MetBuild::Date &startDate,
                 const MetBuild::Date &endDate, unsigned time_step,
                 const std::string &pressureFile);

  ~OwiAsciiDomain() override;

  int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
          &data) override;
  
  int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
          &data) override;

  void open() override;

  void close() override;

 private:
  void write_header();

  static std::string formatHeaderCoordinates(float value);
  static std::string generateHeaderLine(const Date &date1, const Date &date2);
  static std::string generateRecordHeader(const Date &date, const Grid *grid);

  void write_record(
      std::ofstream *stream,
      const std::vector<std::vector<MetBuild::MeteorologicalDataType>> &value)
      const;

  Date m_previousDate;
  std::ofstream m_ofstream_pressure;
  std::ofstream m_ofstream_wind;
  const std::string m_pressureFile;
  const std::string m_windFile;
};
}  // namespace MetBuild

#endif  // METGET_LIBRARY_OWIASCIIDOMAIN_H_
