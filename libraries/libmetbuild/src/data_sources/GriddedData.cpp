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
#include "GriddedData.h"

#include <utility>

#include "Geometry.h"
#include "Logging.h"
#include "Triangulation.h"

using namespace MetBuild;

GriddedData::GriddedData(std::string filename, VariableNames variableNames,
                         VariableUnits variableUnits)
    : m_ni(0),
      m_nj(0),
      m_size(0),
      m_filenames({std::move(filename)}),
      m_variableNames(std::move(variableNames)),
      m_variableUnits(variableUnits) {}

GriddedData::GriddedData(std::vector<std::string> filenames,
                         VariableNames variableNames,
                         VariableUnits variableUnits)
    : m_ni(0),
      m_nj(0),
      m_size(0),
      m_filenames(std::move(filenames)),
      m_variableNames(std::move(variableNames)),
      m_variableUnits(variableUnits) {}

GriddedData::~GriddedData() = default;

std::vector<std::string> GriddedData::filenames() const { return m_filenames; }

bool GriddedData::point_inside(const Point &p) const {
  return this->m_geometry->is_inside(p);
}

void GriddedData::setNi(size_t ni) { m_ni = ni; }

void GriddedData::setNj(size_t nj) { m_nj = nj; }

void GriddedData::setSize(size_t size) { m_size = size; }

std::vector<double> GriddedData::getVariable1d(
    MetBuild::GriddedDataTypes::VARIABLES v) {
  std::vector<double> vec;
  double unit_conversion = 1.0;
  switch (v) {
    case MetBuild::GriddedDataTypes::VAR_PRESSURE:
      vec = this->getArray1d(m_variableNames.pressure());
      unit_conversion = this->m_variableUnits.pressure();
      break;
    case MetBuild::GriddedDataTypes::VAR_U10:
      vec = this->getArray1d(m_variableNames.u10());
      unit_conversion = this->m_variableUnits.u10();
      break;
    case MetBuild::GriddedDataTypes::VAR_V10:
      vec = this->getArray1d(m_variableNames.v10());
      unit_conversion = this->m_variableUnits.v10();
      break;
    case MetBuild::GriddedDataTypes::VAR_RAINFALL:
      vec = this->getArray1d(m_variableNames.precipitation());
      unit_conversion = this->m_variableUnits.precipitation();
      break;
    case MetBuild::GriddedDataTypes::VAR_HUMIDITY:
      vec = this->getArray1d(m_variableNames.humidity());
      unit_conversion = this->m_variableUnits.humidity();
      break;
    case MetBuild::GriddedDataTypes::VAR_TEMPERATURE:
      vec = this->getArray1d(m_variableNames.temperature());
      unit_conversion = this->m_variableUnits.temperature();
      break;
    case MetBuild::GriddedDataTypes::VAR_ICE:
      vec = this->getArray1d(m_variableNames.ice());
      unit_conversion = this->m_variableUnits.ice();
      break;
    default:
      Logging::throwError("No valid variable specified.");
      return {};
  }

  if (unit_conversion != 1.0) {
    for (auto &vv : vec) {
      vv *= unit_conversion;
    }
  }

  return vec;
};

std::vector<std::vector<double>> GriddedData::getVariable2d(
    MetBuild::GriddedDataTypes::VARIABLES v) {
  switch (v) {
    case MetBuild::GriddedDataTypes::VAR_PRESSURE:
      return this->getArray2d(m_variableNames.pressure());
    case MetBuild::GriddedDataTypes::VAR_U10:
      return this->getArray2d(m_variableNames.u10());
    case MetBuild::GriddedDataTypes::VAR_V10:
      return this->getArray2d(m_variableNames.v10());
    case MetBuild::GriddedDataTypes::VAR_RAINFALL:
      return this->getArray2d(m_variableNames.precipitation());
    case MetBuild::GriddedDataTypes::VAR_HUMIDITY:
      return this->getArray2d(m_variableNames.humidity());
    case MetBuild::GriddedDataTypes::VAR_TEMPERATURE:
      return this->getArray2d(m_variableNames.temperature());
    case MetBuild::GriddedDataTypes::VAR_ICE:
      return this->getArray2d(m_variableNames.ice());
    default:
      Logging::throwError("No valid variable specified.");
      return {};
  }
};

void GriddedData::setCorners(std::array<MetBuild::Point, 4> corners) {
  m_corners = corners;
}

std::array<Point, 4> GriddedData::corners() const { return m_corners; }

void GriddedData::setGeometry(std::unique_ptr<MetBuild::Geometry> &geometry) {
  m_geometry = std::move(geometry);
}

// void GriddedData::setTriangulation(
//     std::unique_ptr<MetBuild::Triangulation> &tri) {
//   m_triangulation = std::move(tri);
// }
// MetBuild::InterpolationWeight GriddedData::interpolationWeight(double x,
//                                                                double y)
//                                                                const {
//   return this->m_triangulation->getInterpolationFactors(x, y);
// }

void GriddedData::setType(const MetBuild::GriddedDataTypes::TYPE &t) {
  m_type = t;
}

MetBuild::GriddedDataTypes::TYPE GriddedData::type() const { return m_type; }

void GriddedData::setSourceSubtype(
    const MetBuild::GriddedDataTypes::SOURCE_SUBTYPE &t) {
  m_sourceSubtype = t;
}

MetBuild::GriddedDataTypes::SOURCE_SUBTYPE GriddedData::sourceSubtype() const {
  return m_sourceSubtype;
}

std::vector<MetBuild::Point> GriddedData::bounding_region() const {
  return m_bounding_region;
}

void GriddedData::set_bounding_region(const std::vector<Point> &region) {
  m_bounding_region = region;
}
