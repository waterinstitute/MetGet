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
#ifndef METGET_SRC_OUTPUTDOMAIN_H_
#define METGET_SRC_OUTPUTDOMAIN_H_

#include "Date.h"
#include "Grid.h"
#include "Logging.h"

namespace MetBuild {
class OutputDomain {
 public:
  OutputDomain(const MetBuild::Grid *grid, const MetBuild::Date &startDate,
               const MetBuild::Date &endDate, const unsigned timestep)
      : m_grid(grid),
        m_startDate(startDate),
        m_endDate(endDate),
        m_timestep(timestep),
        m_isOpen(false) {}

  virtual ~OutputDomain() = default;

  virtual void open() = 0;
  virtual void close() = 0;

  bool is_open() const { return m_isOpen; }

  unsigned timestep() const { return m_timestep; }

  MetBuild::Date startDate() const { return m_startDate; }
  MetBuild::Date endDate() const { return m_endDate; }

  const MetBuild::Grid *grid() const { return m_grid; }

  virtual int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
          &data) {
    metbuild_throw_exception("Function not implemented");
    return 1;
  }

  virtual int write(
      const MetBuild::Date &date,
      const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
          &data) {
    metbuild_throw_exception("Function not implemented");
    return 1;
  }

 protected:
  void set_open(bool status) { m_isOpen = status; }

 private:
  bool m_isOpen;
  const MetBuild::Grid *m_grid;
  const MetBuild::Date m_startDate;
  const MetBuild::Date m_endDate;
  const unsigned m_timestep;
};
}  // namespace MetBuild
#endif  // METGET_SRC_OUTPUTDOMAIN_H_
