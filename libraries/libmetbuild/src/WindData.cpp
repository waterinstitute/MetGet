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
#include "WindData.h"

#include <cassert>

using namespace MetBuild;

WindData::WindData(size_t ni, size_t nj)
    : m_ni(ni),
      m_nj(nj),
      m_u(nj, std::vector<double>(ni, 0.0)),
      m_v(nj, std::vector<double>(ni, 0.0)),
      m_p(nj, std::vector<double>(ni, background_pressure())) {}

const std::vector<std::vector<double>>& WindData::u() const { return m_u; }

const std::vector<std::vector<double>>& WindData::v() const { return m_v; }

const std::vector<std::vector<double>>& WindData::p() const { return m_p; }

void WindData::setU(size_t i, size_t j, double value) {
  assert(i < m_ni);
  assert(j < m_nj);
  m_u[j][i] = value;
}

void WindData::setV(size_t i, size_t j, double value) {
  assert(i < m_ni);
  assert(j < m_nj);
  m_v[j][i] = value;
}

void WindData::setP(size_t i, size_t j, double value) {
  assert(i < m_ni);
  assert(j < m_nj);
  m_p[j][i] = value;
}

void WindData::fill(double value) { this->fill(value, value, value); }

void WindData::fill(double u, double v, double p) {
  for (auto j = 0; j < m_nj; ++j) {
    std::fill(m_u[j].begin(), m_u[j].end(), u);
    std::fill(m_v[j].begin(), m_v[j].end(), v);
    std::fill(m_p[j].begin(), m_p[j].end(), p);
  }
}
