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
#include "Grid.h"

#include <fstream>
#include <iostream>

#include "Geometry.h"
#include "boost/geometry.hpp"

using namespace MetBuild;
namespace bg = boost::geometry;
typedef bg::model::point<double, 2, bg::cs::cartesian> point_t;
typedef bg::model::polygon<point_t> polygon_t;

Grid::Grid(double llx, double lly, double urx, double ury, double dx, double dy)
    : m_di(dx),
      m_dj(dy),
      m_rotation(0.0),
      m_dxx(dx),
      m_dxy(0.0),
      m_dyx(0.0),
      m_dyy(dy),
      m_ni(std::floor((urx - llx) / m_dxx) + 1),
      m_nj(std::floor((ury - lly) / m_dyy) + 1),
      m_width(urx - llx),
      m_height(ury - lly),
      m_center((llx + m_width / 2.0), (lly + m_height / 2.0)),
      m_corners(generateCorners(m_center.x(), m_center.y(), m_width, m_height)),
      m_geometry(std::make_unique<Geometry>(m_corners)) {
  assert(urx > llx);
  assert(lly < ury);
  assert(m_dxx > 0.0);
  assert(m_dyy > 0.0);
  assert(m_ni > 0);
  assert(m_nj > 0);
  assert(m_width > 0);
  assert(m_height > 0);
  this->generateGrid();
}

Grid::Grid(double xinit, double yinit, size_t ni, size_t nj, double di,
           double dj, double rotation)
    : m_di(di),
      m_dj(dj),
      m_rotation(rotation * M_PI / 180.0),
      m_dxx(di * std::cos(m_rotation)),
      m_dxy(di * std::sin(m_rotation)),
      m_dyx(dj * std::sin(m_rotation)),
      m_dyy(dj * std::cos(m_rotation)),
      m_ni(ni),
      m_nj(nj),
      m_width(static_cast<double>(m_ni - 1) * m_dxx),
      m_height(static_cast<double>(m_nj - 1) * m_dyy),
      m_center((xinit + m_width / 2.0), (yinit + m_height / 2.0)),
      m_corners(generateCorners(m_center.x(), m_center.y(), m_width, m_height)),
      m_geometry(std::make_unique<Geometry>(m_corners)) {
  assert(m_di > 0);
  assert(m_dj > 0);
  assert(m_rotation >= -M_PI || m_rotation <= M_PI);
  assert(m_ni > 0);
  assert(m_nj > 0);
  this->generateGrid();
}

Grid::~Grid() = default;

Grid::Grid(const Grid &w)
    : m_di(w.di()),
      m_dj(w.dj()),
      m_rotation(w.rotation() * M_PI / 180.0),
      m_dxx(m_di * std::cos(m_rotation)),
      m_dxy(m_di * std::sin(m_rotation)),
      m_dyx(m_dj * std::sin(m_rotation)),
      m_dyy(m_dj * std::cos(m_rotation)),
      m_ni(w.ni()),
      m_nj(w.nj()),
      m_width(static_cast<double>(m_ni - 1) * m_dxx),
      m_height(static_cast<double>(m_nj - 1) * m_dyy),
      m_center((w.bottom_left().x() + m_width / 2.0),
               (w.bottom_left().y() + m_height / 2.0)),
      m_corners(generateCorners(m_center.x(), m_center.y(), m_width, m_height)),
      m_geometry(std::make_unique<Geometry>(m_corners)) {}

void Grid::generateGrid() {
  m_grid = std::vector<std::vector<Point>>(nj(), std::vector<Point>(ni()));
  for (size_t j = 0; j < nj(); ++j) {
    for (size_t i = 0; i < ni(); ++i) {
      m_grid[j][i] = {bottom_left().x() + i * m_dxx - j * m_dyx,
                      bottom_left().y() + j * m_dyy + i * m_dyx};
    }
  }
}

void Grid::write(const std::string &filename) const {
  std::ofstream fout;
  fout.open(filename);
  size_t count = 0;
  size_t count_i = 0;
  for (auto &i : m_grid) {
    size_t count_j = 0;
    for (auto &j : i) {
      fout << j.x() << " " << j.y() << " " << count << " " << count_i << " "
           << count_j << "\n";
      count++;
      count_j++;
    }
    count_i++;
  }
  fout.close();
}

bool Grid::point_inside(const MetBuild::Point &p) const {
  return this->m_geometry->is_inside(p);
}

std::array<MetBuild::Point, 4> Grid::generateCorners(const double cx,
                                                     const double cy,
                                                     const double w,
                                                     const double h,
                                                     const double rotation) {
  Point top_right(
      cx + ((w / 2.0) * std::cos(rotation)) - ((h / 2.0) * std::sin(rotation)),
      cy + ((w / 2.0) * std::sin(rotation)) + ((h / 2.0) * std::cos(rotation)));

  Point top_left(
      cx - ((w / 2.0) * std::cos(rotation)) - ((h / 2.0) * std::sin(rotation)),
      cy - ((w / 2.0) * std::sin(rotation)) + ((h / 2.0) * std::cos(rotation)));

  Point bottom_left(
      cx - ((w / 2.0) * std::cos(rotation)) + ((h / 2.0) * std::sin(rotation)),
      cy - ((w / 2.0) * std::sin(rotation)) - ((h / 2.0) * std::cos(rotation)));

  Point bottom_right(
      cx + ((w / 2.0) * std::cos(rotation)) + ((h / 2.0) * std::sin(rotation)),
      cy + ((w / 2.0) * std::sin(rotation)) - ((h / 2.0) * std::cos(rotation)));

  return {bottom_left, bottom_right, top_right, top_left};
}
std::vector<double> Grid::x() const {
  std::vector<double> x;
  x.reserve(ni() * nj());
  for (const auto &r : m_grid) {
    for (const auto &c : r) {
      x.push_back(c.x());
    }
  }
  return x;
}

std::vector<double> Grid::y() const {
  std::vector<double> y;
  y.reserve(ni() * nj());
  for (const auto &r : m_grid) {
    for (const auto &c : r) {
      y.push_back(c.y());
    }
  }
  return y;
}