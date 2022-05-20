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
#ifndef METGET_SRC_GRIDDEDDATA_H_
#define METGET_SRC_GRIDDEDDATA_H_

#include <string>
#include <vector>

#include "CppAttributes.h"
#include "Geometry.h"
#include "Kdtree.h"
#include "Point.h"
#include "VariableNames.h"

namespace MetBuild {

class GriddedData {
 public:
  enum TYPE { WIND_PRESSURE, TEMPERATURE, HUMIDITY, RAINFALL, ICE };
  enum VARIABLES {
    VAR_PRESSURE,
    VAR_U10,
    VAR_V10,
    VAR_TEMPERATURE,
    VAR_HUMIDITY,
    VAR_RAINFALL,
    VAR_ICE
  };

  GriddedData(std::string filename, VariableNames variableNames);

  GriddedData(std::vector<std::string> filenames, VariableNames variableNames);

  NODISCARD virtual std::vector<std::vector<double>> latitude2d() = 0;
  NODISCARD virtual const std::vector<double> &latitude1d() const = 0;

  NODISCARD virtual std::vector<std::vector<double>> longitude2d() = 0;
  NODISCARD virtual const std::vector<double> &longitude1d() const = 0;

  NODISCARD std::vector<std::string> filenames() const;

  NODISCARD bool point_inside(const Point &p) const;

  NODISCARD constexpr std::tuple<size_t, size_t> indexToPair(
      size_t index) const {
    size_t j = index % nj();
    size_t i = index / nj();
    return std::make_pair(i, j);
  }

  NODISCARD Point bottom_left() const { return m_corners[0]; }
  NODISCARD Point bottom_right() const { return m_corners[1]; }
  NODISCARD Point top_left() const { return m_corners[3]; }
  NODISCARD Point top_right() const { return m_corners[2]; }

  NODISCARD Kdtree *kdtree() const { return m_tree.get(); }

  NODISCARD constexpr long ni() const { return m_ni; }

  NODISCARD constexpr long nj() const { return m_nj; }

  NODISCARD constexpr size_t size() const { return m_size; }

  NODISCARD VariableNames variableNames() const { return m_variableNames; }

  NODISCARD std::vector<double> getVariable1d(GriddedData::VARIABLES v);

  NODISCARD std::vector<std::vector<double>> getVariable2d(
      GriddedData::VARIABLES v);

 protected:
  virtual void findCorners() = 0;

  void setCorners(std::array<MetBuild::Point, 4> corners);

  void setGeometry(std::unique_ptr<MetBuild::Geometry> &geometry);

  std::array<Point, 4> corners() const;

  void setTree(std::unique_ptr<MetBuild::Kdtree> &tree);

  void setNi(size_t ni);

  void setNj(size_t nj);

  void setSize(size_t size);

  virtual std::vector<double> getArray1d(const std::string &variable) = 0;

  virtual std::vector<std::vector<double>> getArray2d(
      const std::string &variable) = 0;

 private:
  std::vector<std::string> m_filenames;
  size_t m_size;
  long m_ni;
  long m_nj;
  std::unique_ptr<MetBuild::Kdtree> m_tree;
  std::unique_ptr<MetBuild::Geometry> m_geometry;
  std::array<MetBuild::Point, 4> m_corners;
  VariableNames m_variableNames;
};
}  // namespace MetBuild

#endif  // METGET_SRC_GRIDDEDDATA_H_
