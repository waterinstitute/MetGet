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

#include <algorithm>

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

  std::string guessGridUnits(){
    auto ul = this->grid()->top_left();
    auto ur = this->grid()->top_right();
    auto bl = this->grid()->bottom_left();
    auto br = this->grid()->bottom_right();
    std::array<double,4> x = {ul.x(),ur.x(),bl.x(),br.x()};
    std::array<double,4> y = {ul.y(),ur.y(),bl.y(),br.y()};

    auto xmax = std::abs(*std::max_element(x.begin(),x.end()));
    auto xmin = std::abs(*std::min_element(x.begin(),x.end()));
    auto ymax = std::abs(*std::max_element(y.begin(),y.end()));
    auto ymin = std::abs(*std::min_element(y.begin(),y.end()));

    if(xmax > 180.0 || xmin > 180.0 || ymax > 90.0 || ymin > 90.0){
      return "m";
    } else {
      return "deg";
    }
  }

 private:
  bool m_isOpen;
  const MetBuild::Grid *m_grid;
  const MetBuild::Date m_startDate;
  const MetBuild::Date m_endDate;
  const unsigned m_timestep;
};
}  // namespace MetBuild
#endif  // METGET_SRC_OUTPUTDOMAIN_H_
