#ifndef KDTREE_H
#define KDTREE_H

#include <cstddef>
#include <memory>
#include <vector>

namespace MetBuild {

class KdtreePrivate;

class Kdtree {
 public:
  Kdtree();

  Kdtree(const std::vector<double> &x, const std::vector<double> &y);

  ~Kdtree();

  enum _errors { NoError, SizeMismatch };

  size_t size();

  size_t findNearest(double x, double y) const;

  std::vector<std::pair<size_t, double>> findXNearest(double x, double y,
                                                      size_t n) const;

  std::vector<size_t> findWithinRadius(double x, double y, double radius) const;

  bool initialized();

 private:
  std::unique_ptr<KdtreePrivate> m_ptr;
};
}  // namespace MetBuild
#endif  // KDTREE_H
