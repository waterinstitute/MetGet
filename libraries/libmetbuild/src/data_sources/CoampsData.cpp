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
#include "CoampsData.h"

#include <utility>

#include "Triangulation.h"

using namespace MetBuild;

CoampsData::CoampsData(std::vector<std::string> filenames)
    : GriddedData(std::move(filenames),
                  VariableNames("lon", "lat", "slpres", "uuwind", "vvwind",
                                "precip", "relhum", "airtmp", ""),
                  VariableUnits(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)) {
  this->initialize();
  this->setSourceSubtype(MetBuild::GriddedDataTypes::SOURCE_SUBTYPE::COAMPS);
}

void CoampsData::initialize() {
  for (const auto& f : this->filenames()) {
    m_domains.emplace_back(f);
  }
  this->computeMasking();
  this->computeCoordinates();
  this->set_bounding_region(m_domains[0].get_bounding_region());
}

std::vector<std::vector<double>> CoampsData::latitude2d() { return {}; }

const std::vector<double>& CoampsData::latitude1d() const { return m_latitude; }

std::vector<std::vector<double>> CoampsData::longitude2d() { return {}; }

const std::vector<double>& CoampsData::longitude1d() const {
  return m_longitude;
}

void CoampsData::findCorners() { return; }

std::vector<double> CoampsData::getArray1d(const std::string& variable) {
  std::vector<double> result;
  for (const auto& d : m_domains) {
    const auto values = d.get(variable);
    result.reserve(result.size() + values.size());
    result.insert(result.end(), values.begin(), values.end());
  }
  return result;
}

std::vector<std::vector<double>> CoampsData::getArray2d(
    const std::string& variable) {
  return {};
}

void CoampsData::computeMasking() {
  size_t nmask = 0;
  for (size_t dom = 0; dom < m_domains.size() - 1; ++dom) {
    for (size_t p = 0; p < m_domains[dom].size(); ++p) {
      const auto point =
          Point(m_domains[dom].longitude(p), m_domains[dom].latitude(p));
      for (auto inner_dom = dom + 1; inner_dom < m_domains.size();
           ++inner_dom) {
        if (point.x() >= m_domains[inner_dom].point_ll().x() &&
            point.x() <= m_domains[inner_dom].point_ur().x() &&
            point.y() >= m_domains[inner_dom].point_ll().y() &&
            point.y() <= m_domains[inner_dom].point_ur().y()) {
          m_domains[dom].setMask(p, true);
          nmask++;
        }
      }
    }
  }
}

void CoampsData::computeCoordinates() {
  for (auto& d : m_domains) {
    const auto [lon, lat] = d.getUnmaskedCoordinates();
    m_longitude.insert(m_longitude.end(), lon.begin(), lon.end());
    m_latitude.insert(m_latitude.end(), lat.begin(), lat.end());
  }
  this->setSize(m_longitude.size());
  this->setNi(0);
  this->setNj(0);
}

Triangulation CoampsData::generate_triangulation() const {
  return {m_longitude, m_latitude, this->bounding_region()};
}
