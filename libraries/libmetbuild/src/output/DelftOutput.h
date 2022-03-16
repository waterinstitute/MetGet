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
#ifndef METGET_SRC_OUTPUT_DELFTOUTPUT_H_
#define METGET_SRC_OUTPUT_DELFTOUTPUT_H_

#include "OutputFile.h"

namespace MetBuild {

class DelftOutput : public OutputFile {
 public:
  DelftOutput(const MetBuild::Date &date_start, const MetBuild::Date &date_end,
              unsigned time_step, std::string filename,
              bool use_compression = false);

  ~DelftOutput() = default;

  std::vector<std::string> filenames() const override;

  void addDomain(const MetBuild::Grid &w,
                 const std::vector<std::string> &variables) override;

  int write(
      const MetBuild::Date &date, size_t domain_index,
      const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
          &data) override;

  int write(
      const MetBuild::Date &date, size_t domain_index,
      const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
          &data) override;

 private:
  const std::string m_filename;
  const bool m_use_compression;
};
}  // namespace MetBuild

#endif  // METGET_SRC_OUTPUT_DELFTOUTPUT_H_
