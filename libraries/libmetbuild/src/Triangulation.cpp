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
