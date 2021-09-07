
#ifndef METGET_WINDGRID_H
#define METGET_WINDGRID_H

#include <array>
#include <cassert>
#include <cmath>
#include <memory>
#include <string>
#include <vector>

#include "Point.h"

namespace MetBuild {

class Geometry;

class WindGrid {
 public:
  using grid = std::vector<std::vector<MetBuild::Point>>;

  WindGrid(double llx, double lly, double urx, double ury, double dx,
           double dy);
  WindGrid(double xinit, double yinit, size_t ni, size_t nj, double dx,
           double dy, double rotation = 0.0);

  ~WindGrid();

  WindGrid(const WindGrid &w);

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
    return {(m_grid[i][j].x() + m_grid[i + i][j + 1].x()) / 2.0,
            (m_grid[i][j].y() + m_grid[i + 1][j + 1].y()) / 2.0};
  }

  Point corner(const size_t i, const size_t j) const {
    assert(i < ni() && j < nj());
    return {m_grid[i][j].x(), m_grid[i][j].y()};
  }

  bool point_inside(const MetBuild::Point &p) const;

  void write(const std::string &filename) const;

  const grid &grid_positions() const { return m_grid; };

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

#endif  // METGET_WINDGRID_H
