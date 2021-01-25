
#include "Kdtree.h"

#include "KdtreePrivate.h"

using namespace MetBuild;

/**
 * @brief Default constructor for a new Kdtree object
 */
Kdtree::Kdtree() : m_ptr(new KdtreePrivate()) {}

Kdtree::Kdtree(const std::vector<double> &x, const std::vector<double> &y)
    : m_ptr(new KdtreePrivate(x, y)) {}

/**
 * @brief Get the number of nodes in the kdtree point cloud
 * @return Size of kdtree
 */
size_t Kdtree::size() { return this->m_ptr->size(); }

/**
 * @brief Finds the nearest position in the x, y 2d pointcloud
 * @param[in] x x-location for search
 * @param[in] y y-location for search
 * @return index in x,y array
 */
size_t Kdtree::findNearest(const double x, const double y) const {
  return this->m_ptr->findNearest(x, y);
}

/**
 * @brief Finds the nearest 'x' number of locations, sorted
 * @param[in] x x-location for search
 * @param[in] y y-location for search
 * @param[in] n number of points to return
 * @return vector of indices in the x,y array
 */
std::vector<std::pair<size_t, double>> Kdtree::findXNearest(
    const double x, const double y, const size_t n) const {
  return this->m_ptr->findXNearest(x, y, n);
}

/**
 * @brief Checks if the Kdtree has been initialized
 * @return true if the Kdtree has been initialized
 */
bool Kdtree::initialized() { return this->m_ptr->initialized(); }

/**
 * @brief Finds all points within a given radius
 * @param[in] x x-location for search
 * @param[in] y y-location for search
 * @param[in] radius search radius in native coordinates
 * @return vector with indices of found points
 */
std::vector<size_t> Kdtree::findWithinRadius(const double x, const double y,
                                             const double radius) const {
  return this->m_ptr->findWithinRadius(x, y, radius);
}
