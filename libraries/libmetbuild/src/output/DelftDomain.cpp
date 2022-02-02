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
#include "DelftDomain.h"

#include <utility>

#include "boost/algorithm/string.hpp"
#include "boost/format.hpp"

using namespace MetBuild;

DelftDomain::DelftDomain(const MetBuild::Grid *grid,
                         const MetBuild::Date &startDate,
                         const MetBuild::Date &endDate, unsigned int time_step,
                         std::string filename,
                         std::vector<std::string> variables)
    : m_baseFilename(std::move(filename)),
      m_variables(std::move(variables)),
      OutputDomain(grid, startDate, endDate, time_step) {
    this->open();      
}

DelftDomain::~DelftDomain() {
  for (auto &s : m_ofstreams) {
    s.close();
  }
}

std::string DelftDomain::guessGridUnits(){
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

void DelftDomain::open() {
  this->m_filenames.reserve(m_variables.size());
  this->m_ofstreams.reserve(m_variables.size());
  const auto grid_unit = this->guessGridUnits();
  for (const auto &v : m_variables) {
    std::string filename, variableName, units;
    double multiplier;
    std::tie(filename, variableName, units, multiplier) = this->variableToFields(v);
    this->m_filenames.push_back(filename);
    this->m_ofstreams.emplace_back(this->m_filenames.back());
    this->writeHeader(m_ofstreams.back(), variableName, units, grid_unit);
  }
}

void DelftDomain::close() {
  for (auto &s : m_ofstreams) {
    s.close();
  }
}

int DelftDomain::write(
    const MetBuild::Date &date,
    const MetBuild::MeteorologicalData<1, MetBuild::MeteorologicalDataType>
        &data) {
  std::string filename, variableName, units;
  double multiplier;
  std::tie(filename, variableName, units, multiplier) = this->variableToFields(m_variables[0]);
  return this->writeField(m_ofstreams[0], date, data[0]);
}

int DelftDomain::write(
    const MetBuild::Date &date,
    const MetBuild::MeteorologicalData<3, MetBuild::MeteorologicalDataType>
        &data) {
  int return_val = 0;
  for (size_t i = 0; i < 3; ++i) {
    std::string filename, variableName, units;
    double multiplier;
    std::tie(filename, variableName, units, multiplier) = this->variableToFields(m_variables[i]);
    return_val += this->writeField(m_ofstreams[i], date, data[i], multiplier);
  }
  return return_val;
}

std::tuple<std::string, std::string, std::string, double> DelftDomain::variableToFields(
    const std::string &variable) {
  auto v2 = boost::to_lower_copy(variable);
  if (variable == "wind_u") {
    return {this->m_baseFilename + ".amu", "x_wind", "m s-1", 1.0};
  } else if (variable == "wind_v") {
    return {this->m_baseFilename + ".amv", "y_wind", "m s-1", 1.0};
  } else if (variable == "mslp") {
    return {this->m_baseFilename + ".amp", "air_pressure", "Pa", 100.0};
  } else if (variable == "temperature") {
    return {this->m_baseFilename + ".amt", "temperature", "k", 1.0};
  } else if (variable == "humidity") {
    return {this->m_baseFilename + ".amh", "relative_humidity", "%", 1.0};
  } else if (variable == "ice") {
    return {this->m_baseFilename + ".ami", "ice_concentration", "%", 1.0};
  } else if (variable == "rain") {
    return {this->m_baseFilename + ".amr", "precipitation", "mm s-1", 1.0};
  } else {
    metbuild_throw_exception("Invalid variable "+variable+" specified.");
    return {};
  }
}

void DelftDomain::writeHeader(std::ofstream &stream,
                              const std::string &variable,
                              const std::string &units,
			      const std::string &grid_unit) {

  // clang-format off
  stream << std::string("### START OF HEADER\n") +
            "### This file generated by MetGet\n" +
            "### File generated: " + Date::now().toString() + "\n" +
            "FileVersion      = 1.03\n" +
            "filetype         = meteo_on_equidistant_grid\n" +
            "NODATA_value     = "+ boost::str(boost::format("%0.1f") % -999.0) + "\n" +
            "n_cols           = " + boost::str(boost::format("%d")%this->grid()->ni())+"\n"+
            "n_rows           = " + boost::str(boost::format("%d")%this->grid()->nj())+"\n"+
            "grid_unit        = " + grid_unit+"\n" +
            "x_llcorner       = " + boost::str(boost::format("%0.6f")%this->grid()->bottom_left().x())+"\n"+
            "y_llcorner       = " + boost::str(boost::format("%0.6f")%this->grid()->bottom_left().y())+"\n"+
            "dx               = " + boost::str(boost::format("%0.4f")%this->grid()->dx())+"\n"+
            "dy               = " + boost::str(boost::format("%0.4f")%this->grid()->dy())+"\n"+
            "n_quantity       = 1\n"+
            "quantity_1       = "+variable+"\n"+
            "unit_1           = "+units+"\n"+
            "### END OF HEADER\n";
  // clang-format on
}

template <typename T>
int DelftDomain::writeField(std::ofstream &stream, const MetBuild::Date &date,
                            const std::vector<std::vector<T>> &data, const double multiplier) {
  double hours =
      static_cast<double>(date.toSeconds() - this->startDate().toSeconds()) /
      3600.0;
  stream << "TIME = " << boost::str(boost::format("%0.6f") % hours)
         << " hours since " << this->startDate().toString() + " +00:00\n";
  for (const auto &r : data) {
    for (const auto &c : r) {
      stream << boost::str(boost::format("%0.6f ") % (c*multiplier));
    }
    stream << "\n";
  }
  return 0;
}
