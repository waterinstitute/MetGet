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
#include "Grib.h"

#include <cmath>
#include <fstream>
#include <iostream>
#include <utility>

#include "Geometry.h"
#include "GribHandle.h"
#include "Logging.h"
#include "Triangulation.h"
#include "Utilities.h"
#include "boost/algorithm/string/split.hpp"
#include "boost/algorithm/string/trim.hpp"
#include "eccodes.h"

using namespace MetBuild;

Grib::Grib(std::string filename, VariableNames variable_names,
           VariableUnits variable_units, COORDINATE_CONVENTION convention)
    : GriddedData(std::move(filename), std::move(variable_names),
                  variable_units, convention) {
  this->initialize();
  this->setSourceSubtype(MetBuild::GriddedDataTypes::SOURCE_SUBTYPE::GRIB);
}

Grib::~Grib() = default;

const std::vector<double> &Grib::latitude1d() const { return m_latitude; }

const std::vector<double> &Grib::longitude1d() const { return m_longitude; }

std::vector<std::vector<double>> Grib::longitude2d() {
  return mapTo2d(m_longitude, ni(), nj());
}

std::vector<std::vector<double>> Grib::latitude2d() {
  return mapTo2d(m_latitude, ni(), nj());
}

int Grib::getStepLength(const std::string &filename,
                        const std::string &parameter) {
  auto h = GribHandle(filename, parameter);
  std::string p2name;
  size_t p2len = 0;
  CODES_CHECK(codes_get_length(h.ptr(), "stepRange", &p2len), nullptr);
  p2name.resize(p2len, ' ');
  CODES_CHECK(codes_get_string(h.ptr(), "stepRange", &p2name[0], &p2len),
              nullptr);
  boost::trim_if(p2name, Utilities::isNotAlpha);
  boost::trim_if(p2name, boost::is_any_of(" "));
  std::vector<std::string> result;
  boost::algorithm::split(result, p2name, boost::is_any_of("-"),
                          boost::token_compress_off);
  for (auto &s : result) {
    boost::trim_left(s);
  }

  if (result.size() == 1) {
    return 1;
  } else {
    return std::stoi(result[1]) - std::stoi(result[0]);
  }

  metbuild_throw_exception("Could not generate the step range");
  return 0;
}

void Grib::initialize() {
  codes_grib_multi_support_on(grib_context_get_default());

  auto handle = [&](){
    if(Grib::containsVariable(this->filenames()[0], this->variableNames().pressure())) {    
      return GribHandle(this->filenames()[0], this->variableNames().pressure().c_str());
    } else if (Grib::containsVariable(this->filenames()[0], this->variableNames().precipitation())) { 
      return GribHandle(this->filenames()[0], this->variableNames().precipitation().c_str());
    } else {
      metbuild_throw_exception("Could not find a valid variable (tried pressure and precip)");
    }
  }();

  long ni = 0;
  CODES_CHECK(codes_get_long(handle.ptr(), "Ni", &ni), nullptr);
  this->setNi(ni);

  long nj = 0;
  CODES_CHECK(codes_get_long(handle.ptr(), "Nj", &nj), nullptr);
  this->setNj(nj);

  size_t size = 0;
  CODES_CHECK(codes_get_size(handle.ptr(), "values", &size), nullptr);
  this->setSize(size);

  this->readCoordinates(handle.ptr());
  this->findCorners();
}

bool Grib::containsVariable(const std::string &filename,
                            const std::string &name) {
  codes_grib_multi_support_on(grib_context_get_default());
  auto handle = GribHandle(filename, name, true);
  if (handle.ptr()) {
    return true;
  } else {
    return false;
  }
}

std::vector<double> Grib::getArray1d(const std::string &name) {
  if (name.empty()) {
    Logging::throwError("Empty variable specified for read.");
  }
  auto pvm = m_preread_value_map.find(name);
  if (pvm == m_preread_value_map.end()) {
    std::vector<double> arr1d(this->size(), 0.0);
    size_t s = this->size();
    auto handle = GribHandle(this->filenames()[0], name);
    CODES_CHECK(
        codes_get_double_array(handle.ptr(), "values", arr1d.data(), &s),
        nullptr);
    m_preread_values.push_back(arr1d);
    m_preread_value_map[name] = m_preread_values.size() - 1;
    return m_preread_values.back();
  } else {
    return m_preread_values[pvm->second];
  }
}

std::vector<std::vector<double>> Grib::getArray2d(const std::string &name) {
  if (name.empty()) {
    Logging::throwError("Empty variable specified for read.");
  }
  return mapTo2d(this->getArray1d(name), ni(), nj());
}

std::vector<std::vector<double>> Grib::mapTo2d(const std::vector<double> &v,
                                               size_t ni, size_t nj) {
  std::vector<std::vector<double>> arr2d(ni);
  for (size_t i = 0; i < ni; ++i) {
    arr2d[i] = std::vector<double>(nj, 0.0);
  }

  for (size_t i = 0; i < v.size(); ++i) {
    arr2d[i / nj][i % nj] = v[i];
  }
  return arr2d;
}

void Grib::readCoordinates(codes_handle *handle) {
  if (m_latitude.empty()) {
    m_latitude.resize(this->size());
    size_t s = size();
    CODES_CHECK(
        codes_get_double_array(handle, "latitudes", m_latitude.data(), &s),
        nullptr);
  }
  if (m_longitude.empty()) {
    m_longitude.resize(this->size());
    size_t s = this->size();
    CODES_CHECK(
        codes_get_double_array(handle, "longitudes", m_longitude.data(), &s),
        nullptr);
    if (this->convention() == CONVENTION_180) {
      for (auto &v : m_longitude) {
        v = (std::fmod(v + 180.0, 360.0)) - 180.0;
      }
    }
  }
}

void Grib::write_to_ascii(const std::string &filename,
                          const std::string &varname) {
  auto values = this->getArray1d(varname);
  std::ofstream f(filename);
  for (size_t i = 0; i < this->size(); ++i) {
    f << m_longitude[i] << ", " << m_latitude[i] << ", " << values[i] << "\n";
  }
  f.close();
}

void Grib::findCorners() {
  double xtl = *(std::min_element(this->longitude1d().begin(),
                                  this->longitude1d().begin() + ni() - 1));
  double xtr = *(std::max_element(this->longitude1d().begin(),
                                  this->longitude1d().begin() + ni() - 1));
  double xll = *(std::min_element(this->longitude1d().end() - ni(),
                                  this->longitude1d().end()));
  double xlr = *(std::max_element(this->longitude1d().end() - ni(),
                                  this->longitude1d().end()));

  double ytl = *(std::min_element(this->latitude1d().begin(),
                                  this->latitude1d().begin() + ni() - 1));
  double ytr = *(std::max_element(this->latitude1d().begin(),
                                  this->latitude1d().begin() + ni() - 1));
  double yll = *(std::min_element(this->latitude1d().end() - ni(),
                                  this->latitude1d().end()));
  double ylr = *(std::max_element(this->latitude1d().end() - ni(),
                                  this->latitude1d().end()));

  std::array<Point, 4> corners = {Point(xll, yll), Point(xlr, ylr),
                                  Point(xtr, ytr), Point(xtl, ytl)};
  this->setCorners(corners);

  auto geometry = std::make_unique<Geometry>(this->corners());
  this->setGeometry(geometry);
}

Triangulation Grib::generate_triangulation() const {
  return {m_longitude, m_latitude, this->bounding_region()};
}
