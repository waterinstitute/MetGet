//
// Created by Zach Cobell on 5/31/22.
//

#include "Triangulation.h"

#include "TriangulationPrivate.h"

using namespace MetBuild;

MetBuild::Triangulation::Triangulation(
    const std::vector<double>& x, const std::vector<double>& y,
    const std::vector<MetBuild::Point>& bounding_region)
    : m_ptr(std::make_unique<Private::TriangulationPrivate>(x, y,
                                                            bounding_region)) {}

Triangulation::~Triangulation() = default;

Triangulation::Triangulation(const Triangulation& t) {
  m_ptr = std::make_unique<Private::TriangulationPrivate>(*t.m_ptr);
}

MetBuild::InterpolationWeight Triangulation::getInterpolationFactors(
    double x, double y) const {
  return m_ptr->getInterpolationFactors(x, y);
}
