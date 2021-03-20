#ifndef GRIB_H
#define GRIB_H

#include <array>
#include <cstdlib>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "Kdtree.h"
#include "Point.h"

//...Forward Declarations
struct grib_handle;
struct grib_index;
typedef struct grib_handle codes_handle;
typedef struct grib_index codes_index;
typedef struct grib_context codes_context;

namespace MetBuild {

class Geometry;

class Grib {
 public:
  explicit Grib(std::string filename);

  ~Grib();

  size_t size() const;

  std::vector<std::vector<double>> latitude2d();
  const std::vector<double> &latitude1d() const;

  std::vector<std::vector<double>> longitude2d();
  const std::vector<double> &longitude1d() const;

  const Kdtree *kdtree() const;

  long ni() const;

  long nj() const;

  std::tuple<size_t, size_t> indexToPair(size_t index) const;

  std::vector<double> getGribArray1d(const std::string &name);
  std::vector<std::vector<double>> getGribArray2d(const std::string &name);

  std::string filename() const;

  bool point_inside(const Point &p) const;

  Point bottom_left() const { return m_corners[0]; }
  Point bottom_right() const { return m_corners[1]; }
  Point top_left() const { return m_corners[3]; }
  Point top_right() const { return m_corners[2]; }

 private:
  void initialize();
  void readCoordinates(codes_handle *handle);
  void findCorners();
  static std::vector<std::vector<double>> mapTo2d(const std::vector<double> &v,
                                                  size_t ni, size_t nj);
  static codes_handle *make_handle(const std::string &filename, const std::string &name);
  static void close_handle(codes_handle *handle);

  std::string m_filename;
  size_t m_size;
  long m_ni;
  long m_nj;
  std::vector<double> m_latitude;
  std::vector<double> m_longitude;
  std::vector<std::vector<double>> m_preread_values;
  std::unordered_map<std::string, size_t> m_preread_value_map;
  std::unique_ptr<MetBuild::Kdtree> m_tree;
  std::unique_ptr<MetBuild::Geometry> m_geometry;
  std::unique_ptr<FILE *> m_file;
  std::array<MetBuild::Point, 4> m_corners;
  int m_convention;
};
}  // namespace MetBuild
#endif  // GRIB_H
