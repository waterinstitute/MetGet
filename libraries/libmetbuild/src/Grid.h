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
#ifndef METGET_GRID_H
#define METGET_GRID_H

#include <array>
#include <cassert>
#include <cmath>
#include <memory>
#include <string>
#include <vector>

#include "Point.h"

namespace MetBuild {

class Geometry;

class Grid {
 public:
  using grid = std::vector<std::vector<MetBuild::Point>>;

  Grid(double llx, double lly, double urx, double ury, double dx,
           double dy);
  Grid(double xinit, double yinit, size_t ni, size_t nj, double dx,
           double dy, double rotation = 0.0);

  ~Grid();

  Grid(const Grid &w);

  constexpr size_t ni() const { return m_ni; }
  constexpr size_t nj() const { return m_nj; }
  constexpr double rotation() const { return m_rotation * 180.0 / M_PI; }
  constexpr double di() const { return m_di; }
  constexpr double dj() const { return m_dj; }
  constexpr double dxx() const { return m_dxx; }
  constexpr double dxy() const { return m_dxy; }
  constexpr double dyx() const { return m_dyx; }
  constexpr double dyy() const { return m_dyy; }
  constexpr double dx() const { return m_dxx; }
  constexpr double dy() const { return m_dyy; }
  constexpr Point bottom_left() const { return m_corners[0]; }
  constexpr Point bottom_right() const { return m_corners[1]; }
  constexpr Point top_left() const { return m_corners[3]; }
  constexpr Point top_right() const { return m_corners[2]; }

  Point center(const size_t i, const size_t j) const {
    assert(i < ni() - 1 && j < nj() - 1);
    if (i > ni() - 1 || j > nj() + 1) return {0, 0};
    return {(m_grid[j][i].x() + m_grid[j + 1][i + 1].x()) / 2.0,
            (m_grid[j][i].y() + m_grid[j + 1][i + 1].y()) / 2.0};
  }

  Point corner(const size_t i, const size_t j) const {
    assert(i < ni() && j < nj());
    return {m_grid[j][i].x(), m_grid[j][i].y()};
  }

  bool point_inside(const MetBuild::Point &p) const;

  void write(const std::string &filename) const;

  const grid &grid_positions() const { return m_grid; };

  std::vector<double> x() const;
  std::vector<double> y() const;
  
  std::vector<double> xcolumn() const;
  std::vector<double> ycolumn() const;

 private:
  const double m_di;
  const double m_dj;
  const double m_rotation;
  const double m_dxx;
  const double m_dxy;
  const double m_dyx;
  const double m_dyy;
  const size_t m_ni;
  const size_t m_nj;
  const double m_width;
  const double m_height;
  const Point m_center;
  const std::array<Point, 4> m_corners;

  grid m_grid;

  std::unique_ptr<MetBuild::Geometry> m_geometry;

  void generateGrid();
  static std::array<MetBuild::Point, 4> generateCorners(double cx, double cy,
                                                        double w, double h,
                                                        double rotation = 0.0);
};

}  // namespace MetBuild

#endif  // METGET_Grid_H
