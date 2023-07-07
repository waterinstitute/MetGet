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
#include "TriangulationPrivate.h"

#include <fstream>
#include <limits>
#include <utility>

#define FMT_HEADER_ONLY

#include "Logging.h"
#include "fmt/core.h"

using namespace MetBuild::Private;

TriangulationPrivate::TriangulationPrivate(
    const std::vector<double> &x, const std::vector<double> &y,
    const std::vector<MetBuild::Point> &bounding_region)
    : m_bounding_region(bounding_region) {
  assert(x.size() == y.size());
  m_points.reserve(x.size());
  for (size_t i = 0; i < x.size(); ++i) {
    m_points.emplace_back(x[i], y[i]);
  }

  const auto boundary_polygon =
      MetBuild::Private::TriangulationPrivate::construct_boundary_polygon(
          bounding_region);
  this->construct_triangulation(boundary_polygon);
  // this->write("triangulation.14");
}

TriangulationPrivate::TriangulationPrivate(
    std::vector<MetBuild::Point> p,
    const std::vector<MetBuild::Point> &bounding_region)
    : m_points(std::move(p)), m_bounding_region(bounding_region) {
  const auto boundary_polygon =
      MetBuild::Private::TriangulationPrivate::construct_boundary_polygon(
          bounding_region);
  this->construct_triangulation(boundary_polygon);
  // this->write("triangulation.14");
}

TriangulationPrivate::Polygon_t
TriangulationPrivate::construct_boundary_polygon(
    const std::vector<MetBuild::Point> &bounding_region) {
  Polygon_t poly;
  for (const auto &p : bounding_region) {
    poly.push_back(Point_t(p.x(), p.y()));
  }
  return poly;
}

//...Algorithm copied from CGAL example
void TriangulationPrivate::mark_domains(
    DelaunayTriangulation_t::Face_handle start, int index,
    std::list<DelaunayTriangulation_t::Edge> &border) {
  if (start->info().nesting_level != -1) {
    return;
  }
  std::list<DelaunayTriangulation_t::Face_handle> queue;
  queue.push_back(start);
  while (!queue.empty()) {
    auto fh = queue.front();
    queue.pop_front();
    if (fh->info().nesting_level == -1) {
      fh->info().nesting_level = index;
      for (int i = 0; i < 3; i++) {
        DelaunayTriangulation_t::Edge e(fh, i);
        auto n = fh->neighbor(i);
        if (n->info().nesting_level == -1) {
          if (m_triangulation.is_constrained(e))
            border.push_back(e);
          else
            queue.push_back(n);
        }
      }
    }
  }
}

void TriangulationPrivate::trim_mesh() {
  std::list<DelaunayTriangulation_t::Edge> border;
  this->mark_domains(m_triangulation.infinite_face(), 0, border);
  while (!border.empty()) {
    auto e = border.front();
    border.pop_front();
    auto n = e.first->neighbor(e.second);
    if (n->info().nesting_level == -1) {
      this->mark_domains(n, e.first->info().nesting_level + 1, border);
    }
  }
}

void TriangulationPrivate::construct_triangulation(const Polygon_t &polygon) {
  std::vector<std::pair<Point_t, size_t>> coordinates;
  coordinates.reserve(m_points.size());

  size_t idx = 0;
  for (const auto &p : m_points) {
    coordinates.emplace_back(Point_t(p.x(), p.y()), idx);
    idx++;
  }

  m_triangulation.insert_constraint(polygon.vertices_begin(),
                                    polygon.vertices_end(), true);
  m_triangulation.insert(coordinates.begin(), coordinates.end());

  //...Remove the triangles that are not within the domain
  // sets the face->info()->in_domain() attribute to false
  this->trim_mesh();

  //...CGAL will handle duplicate points, but we cannot, so if we
  // made a mistake earlier, this will stop here
  if (m_points.size() != m_triangulation.number_of_vertices()) {
    std::cerr << "Number of points: " << m_points.size() << ", "
              << "Expected number of points: "
              << m_triangulation.number_of_vertices() << std::endl;
    Logging::throwError(
        "The domain appears to contain duplicated points. This error is "
        "internal and fatal.");
  }
}

MetBuild::InterpolationWeight TriangulationPrivate::getInterpolationFactors(
    double x, double y) const {
  const Point_t pt(x, y);

  using CartesianKernel = CGAL::Simple_cartesian<double>;
  using FT = CartesianKernel::FT;
  using Point_2 = CartesianKernel::Point_2;

  DelaunayTriangulation_t::Locate_type locate_type =
      DelaunayTriangulation_t::OUTSIDE_AFFINE_HULL;
  int dmy_int = 0;
  const auto fh = m_triangulation.locate(pt, locate_type, dmy_int);
  if (fh->info().in_domain() &&
      (locate_type == DelaunayTriangulation_t::FACE ||
       locate_type == DelaunayTriangulation_t::EDGE ||
       locate_type == DelaunayTriangulation_t::VERTEX)) {
    const Point_2 p_query(pt.x(), pt.y());

    const Point_2 p0(fh->vertex(0)->point().x(), fh->vertex(0)->point().y());
    const Point_2 p1(fh->vertex(1)->point().x(), fh->vertex(1)->point().y());
    const Point_2 p2(fh->vertex(2)->point().x(), fh->vertex(2)->point().y());

    std::vector<FT> result;
    result.reserve(3);

    CGAL::Barycentric_coordinates::triangle_coordinates_2(
        p0, p1, p2, p_query, std::back_inserter(result));

    std::array<size_t, 3> n = {fh->vertex(0)->info(), fh->vertex(1)->info(),
                               fh->vertex(2)->info()};

    return {n, {result[0], result[1], result[2]}};
  }
  return {{TriangulationPrivate::invalid_point(),
           TriangulationPrivate::invalid_point(),
           TriangulationPrivate::invalid_point()},
          {0.0, 0.0, 0.0}};
}

void TriangulationPrivate::write(const std::string &filename) const {
  std::ofstream out(filename);
  const std::string header = "CGAL triangulation\n";
  const std::string sizing = fmt::format(
      "{:d}  {:d}\n", m_triangulation.number_of_faces(), m_points.size());
  out << header;
  out << sizing;

  size_t idx = 0;
  for (const auto &p : m_points) {
    idx++;
    const std::string point_line =
        fmt::format("{:d} {:0.9f} {:0.9f} 0.0\n", idx, p.x(), p.y());
    out << point_line;
  }

  idx = 0;
  for (const auto &f : m_triangulation.all_face_handles()) {
    if (f->info().in_domain()) {
      idx++;
      size_t n0 = f->vertex(0)->info() + 1;
      size_t n1 = f->vertex(1)->info() + 1;
      size_t n2 = f->vertex(2)->info() + 1;
      const std::string face_line =
          fmt::format("{:d} 3 {:d} {:d} {:d}\n", idx, n0, n1, n2);
      out << face_line;
    }
  }
  out << "0 \n 0 \n 0 \n 0 \n";
  out.close();
}
