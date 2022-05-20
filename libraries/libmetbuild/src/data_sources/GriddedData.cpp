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

#include "Logging.h"

using namespace MetBuild;

GriddedData::GriddedData(std::string filename, VariableNames variableNames)
    : m_filenames({std::move(filename)}),
      m_variableNames(std::move(variableNames)),
      m_ni(0),
      m_nj(0),
      m_size(0) {}

GriddedData::GriddedData(std::vector<std::string> filenames,
                         VariableNames variableNames)
    : m_filenames(std::move(filenames)),
      m_variableNames(std::move(variableNames)),
      m_ni(0),
      m_nj(0),
      m_size(0) {}

std::vector<std::string> GriddedData::filenames() const { return m_filenames; }

bool GriddedData::point_inside(const Point &p) const {
  return this->m_geometry->is_inside(p);
}

void GriddedData::setTree(std::unique_ptr<MetBuild::Kdtree> &tree) {
  m_tree = std::move(tree);
}

void GriddedData::setNi(size_t ni) { m_ni = ni; }

void GriddedData::setNj(size_t nj) { m_nj = nj; }

void GriddedData::setSize(size_t size) { m_size = size; }

std::vector<double> GriddedData::getVariable1d(VARIABLES v) {
  switch (v) {
    case GriddedData::VAR_PRESSURE:
      return this->getArray1d(m_variableNames.pressure());
    case GriddedData::VAR_U10:
      return this->getArray1d(m_variableNames.u10());
    case GriddedData::VAR_V10:
      return this->getArray1d(m_variableNames.v10());
    case GriddedData::VAR_RAINFALL:
      return this->getArray1d(m_variableNames.precipitation());
    case GriddedData::VAR_HUMIDITY:
      return this->getArray1d(m_variableNames.humidity());
    case GriddedData::VAR_TEMPERATURE:
      return this->getArray1d(m_variableNames.temperature());
    case GriddedData::VAR_ICE:
      return this->getArray1d(m_variableNames.ice());
    default:
      Logging::throwError("No valid variable specified.");
      return {};
  }
};

std::vector<std::vector<double>> GriddedData::getVariable2d(VARIABLES v) {
  switch (v) {
    case GriddedData::VAR_PRESSURE:
      return this->getArray2d(m_variableNames.pressure());
    case GriddedData::VAR_U10:
      return this->getArray2d(m_variableNames.u10());
    case GriddedData::VAR_V10:
      return this->getArray2d(m_variableNames.v10());
    case GriddedData::VAR_RAINFALL:
      return this->getArray2d(m_variableNames.precipitation());
    case GriddedData::VAR_HUMIDITY:
      return this->getArray2d(m_variableNames.humidity());
    case GriddedData::VAR_TEMPERATURE:
      return this->getArray2d(m_variableNames.temperature());
    case GriddedData::VAR_ICE:
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