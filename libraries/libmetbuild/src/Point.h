//
// Created by Zach Cobell on 1/22/21.
//

#ifndef METGET_LIBRARY_POINT_H_
#define METGET_LIBRARY_POINT_H_

namespace MetBuild {

class Point {
 public:
  constexpr Point(double x = 0.0, double y = 0.0) : m_x(x), m_y(y) {}

  constexpr double x() const { return m_x; }

  constexpr double y() const { return m_y; }

  void setX(double x) { m_x = x; }

  void setY(double y) { m_y = y; }

 private:
  double m_x;
  double m_y;
};

}  // namespace MetBuild

#endif  // METGET_LIBRARY_POINT_H_
