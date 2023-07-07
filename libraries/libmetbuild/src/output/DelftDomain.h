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
#ifndef METGET_SRC_OUTPUT_DELFTDOMAIN_H_
#define METGET_SRC_OUTPUT_DELFTDOMAIN_H_

#include <fstream>
#include <utility>

#include "MeteorologicalData.h"
#include "OutputDomain.h"

namespace MetBuild {

class DelftDomain : public OutputDomain {
 public:
  DelftDomain(const MetBuild::Grid *grid, const MetBuild::Date &startDate,
              const MetBuild::Date &endDate, unsigned time_step,
              std::string filename, std::vector<std::string> variables,
              bool use_compression = false);

  ~DelftDomain() override;

  void open() override;

  void close() override;

  int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
          &data) override;

  int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
          &data) override;

 private:
  void _open();
  void _close();

  std::tuple<std::string, std::string, std::string, double> variableToFields(
      const std::string &variable);

  void writeHeader(std::ostream *stream, const std::string &variable,
                   const std::string &units, const std::string &grid_unit);

  template <typename T>
  int writeField(std::ostream *stream, const MetBuild::Date &date,
                 const std::vector<std::vector<T>> &data,
                 double multiplier = 1.0);

  const std::vector<std::string> m_variables;
  const std::string m_baseFilename;
  std::vector<std::ofstream> m_ofstreams;
  std::vector<std::unique_ptr<boost::iostreams::filtering_streambuf<
      boost::iostreams::output, char, std::char_traits<char>,
      std::allocator<char>, boost::iostreams::public_>>>
      m_compressedio_buffer;
  std::vector<std::unique_ptr<std::ostream>> m_ostreams;
  const bool m_use_compression;
  const int m_default_compression_level;
};

}  // namespace MetBuild
#endif  // METGET_SRC_OUTPUT_DELFTDOMAIN_H_
