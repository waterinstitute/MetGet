//
// Created by Zach Cobell on 5/25/22.
//

#ifndef METGET_SRC_TRIANGULATIONPRIVATE_H_
#define METGET_SRC_TRIANGULATIONPRIVATE_H_

#include <cstdlib>
#include <limits>
#include <memory>
#include <vector>

#include "CGAL/Barycentric_coordinates_2/triangle_coordinates_2.h"
#include "CGAL/Constrained_Delaunay_triangulation_2.h"
#include "CGAL/Delaunay_mesh_face_base_2.h"
#include "CGAL/Exact_predicates_inexact_constructions_kernel.h"
#include "CGAL/Polygon_2.h"
#include "CGAL/Triangulation_face_base_with_info_2.h"
#include "CGAL/Triangulation_vertex_base_with_info_2.h"
#include "InterpolationWeight.h"
#include "Point.h"

namespace MetBuild::Private {

class TriangulationPrivate {
  struct FaceInfo2 {
    FaceInfo2() : nesting_level(-1) {}
    int nesting_level;
    [[nodiscard]] bool in_domain() const { return nesting_level % 2 == 1; }
  };

  // CGAL Types used within
  typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel_t;
  typedef CGAL::Triangulation_vertex_base_with_info_2<size_t, Kernel_t>
      Vertex_t;
  typedef CGAL::Triangulation_face_base_with_info_2<FaceInfo2, Kernel_t> Face_t;
  typedef CGAL::Constrained_triangulation_face_base_2<Kernel_t, Face_t>
      ConstrainedFace_t;
  typedef CGAL::Delaunay_mesh_face_base_2<Kernel_t, ConstrainedFace_t>
      Delaunay_Face_t;
  typedef CGAL::Triangulation_data_structure_2<Vertex_t, Delaunay_Face_t>
      TriangulationDataStructure_t;
  typedef CGAL::Constrained_Delaunay_triangulation_2<
      Kernel_t, TriangulationDataStructure_t>
      DelaunayTriangulation_t;
  typedef Kernel_t::Point_2 Point_t;
  typedef CGAL::Polygon_2<Kernel_t> Polygon_t;

 public:
  TriangulationPrivate(const std::vector<double> &x,
                       const std::vector<double> &y,
                       const std::vector<MetBuild::Point> &bounding_region);

  TriangulationPrivate(std::vector<MetBuild::Point> p,
                       const std::vector<MetBuild::Point> &bounding_region);

  static constexpr size_t invalid_point() {
    return std::numeric_limits<size_t>::max();
  }

  [[nodiscard]] MetBuild::InterpolationWeight getInterpolationFactors(
      double x, double y) const;

  std::vector<MetBuild::Point> points() const;

  std::vector<MetBuild::Point> bounding_region() const;

 private:
  void write(const std::string &filename) const;

  void construct_triangulation(const Polygon_t &polygon);

  void trim_mesh();

  void mark_domains(DelaunayTriangulation_t::Face_handle start, int index,
                    std::list<DelaunayTriangulation_t::Edge> &border);

  static Polygon_t construct_boundary_polygon(
      const std::vector<MetBuild::Point> &bounding_region);

  std::vector<Point> m_points;
  std::vector<Point> m_bounding_region;
  DelaunayTriangulation_t m_triangulation;
};
}  // namespace MetBuild::Private

#endif  // METGET_SRC_TRIANGULATIONPRIVATE_H_
