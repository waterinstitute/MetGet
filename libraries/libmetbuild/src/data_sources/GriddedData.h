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

#include <memory>
#include <string>
#include <tuple>
#include <vector>

#include "CppAttributes.h"
#include "GriddedDataTypes.h"
#include "InterpolationWeight.h"
#include "Point.h"
#include "VariableNames.h"

namespace MetBuild {

class Geometry;
class Kdtree;
class Triangulation;

class GriddedData {
 public:
  GriddedData() = default;

  GriddedData(std::string filename, MetBuild::VariableNames variableNames);

  GriddedData(std::vector<std::string> filenames,
              MetBuild::VariableNames variableNames);

  virtual ~GriddedData();

  virtual std::vector<std::vector<double>> latitude2d() = 0;
  virtual const std::vector<double> &latitude1d() const = 0;

  virtual std::vector<std::vector<double>> longitude2d() = 0;
  virtual const std::vector<double> &longitude1d() const = 0;

  std::vector<std::string> filenames() const;

  bool point_inside(const Point &p) const;

  constexpr std::tuple<size_t, size_t> indexToPair(size_t index) const {
    size_t j = index % nj();
    size_t i = index / nj();
    return std::make_tuple(i, j);
  }

  Point bottom_left() const { return m_corners[0]; }
  Point bottom_right() const { return m_corners[1]; }
  Point top_left() const { return m_corners[3]; }
  Point top_right() const { return m_corners[2]; }

  constexpr long ni() const { return m_ni; }

  constexpr long nj() const { return m_nj; }

  constexpr size_t size() const { return m_size; }

  MetBuild::VariableNames variableNames() const { return m_variableNames; }

  std::vector<double> getVariable1d(MetBuild::GriddedDataTypes::VARIABLES v);

  std::vector<std::vector<double>> getVariable2d(MetBuild::GriddedDataTypes::VARIABLES v);

  // MetBuild::InterpolationWeight interpolationWeight(double x, double y)
  // const;

  MetBuild::GriddedDataTypes::TYPE type() const;

  MetBuild::GriddedDataTypes::SOURCE_SUBTYPE sourceSubtype() const;

  virtual Triangulation generate_triangulation() const = 0;

 protected:
  virtual void findCorners() = 0;

  void setType(const GriddedDataTypes::TYPE &t);

  void setSourceSubtype(const GriddedDataTypes::SOURCE_SUBTYPE &t);

  void setCorners(std::array<MetBuild::Point, 4> corners);

  void setGeometry(std::unique_ptr<MetBuild::Geometry> &geometry);

  std::array<Point, 4> corners() const;

  void setNi(size_t ni);

  void setNj(size_t nj);

  void setSize(size_t size);

  virtual std::vector<double> getArray1d(const std::string &variable) = 0;

  virtual std::vector<std::vector<double>> getArray2d(
      const std::string &variable) = 0;

  std::vector<MetBuild::Point> bounding_region() const;

 protected:
  void set_bounding_region(const std::vector<Point> &region);

 private:
  GriddedDataTypes::TYPE m_type;
  GriddedDataTypes::SOURCE_SUBTYPE m_sourceSubtype;
  long m_ni;
  long m_nj;
  size_t m_size;
  std::vector<MetBuild::Point> m_bounding_region;
  std::vector<std::string> m_filenames;
  std::unique_ptr<MetBuild::Geometry> m_geometry;
  std::array<MetBuild::Point, 4> m_corners;
  MetBuild::VariableNames m_variableNames;
};
}  // namespace MetBuild

#endif  // METGET_SRC_GRIDDEDDATA_H_
