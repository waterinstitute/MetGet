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
#ifndef KDTREE_PRIVATE_H
#define KDTREE_PRIVATE_H

#include <cstdlib>
#include <memory>
#include <vector>

#include "nanoflann.hpp"

namespace MetBuild {

class KdtreePrivate {
 public:
  KdtreePrivate();

  KdtreePrivate(const std::vector<double> &x, const std::vector<double> &y);

  bool initialized() const;

  size_t size() const;

  size_t findNearest(double x, double y) const;

  std::vector<std::pair<size_t, double>> findXNearest(double x, double y,
                                                      size_t n) const;

  std::vector<size_t> findWithinRadius(double x, double y, double radius) const;

 private:
  int build(const std::vector<double> &x, const std::vector<double> &y);

  bool m_initialized;

  template <typename T>
  struct PointCloud {
    struct Point {
      T x, y;
    };

    std::vector<Point> pts;

    // Must return the number of data points
    inline size_t kdtree_get_point_count() const { return pts.size(); }

    // Returns the dim'th component of the idx'th point in the class:
    // Since this is inlined and the "dim" argument is typically an immediate
    // value, the
    //  "if/else's" are actually solved at compile time.
    inline T kdtree_get_pt(const size_t idx, const size_t dim) const {
      if (dim == 0)
        return pts[idx].x;
      else
        return pts[idx].y;
    }

    // Optional bounding-box computation: return false to default to a standard
    // bbox computation loop.
    //   Return true if the BBOX was already computed by the class and returned
    //   in "bb" so it can be avoided to redo it again. Look at bb.size() to
    //   find out the expected dimensionality (e.g. 2 or 3 for point clouds)
    template <class BBOX>
    bool kdtree_get_bbox(BBOX & /* bb */) const {
      return false;
    }
  };

  // construct a kd-tree index:
  typedef nanoflann::KDTreeSingleIndexAdaptor<
      nanoflann::L2_Simple_Adaptor<double, PointCloud<double>>,
      PointCloud<double>, 2>
      kd_tree_t;

  PointCloud<double> m_cloud;
  std::unique_ptr<kd_tree_t> m_tree;
  const nanoflann::SearchParams m_params;
};
}  // namespace MetBuild

#endif  // KDTREE_PRIVATE_H
