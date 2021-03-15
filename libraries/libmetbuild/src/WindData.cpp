//
// Created by Zach Cobell on 1/21/21.
//

#include "WindData.h"
#include <cassert>

using namespace MetBuild;

WindData::WindData(size_t n)
    : m_n(n), m_u(n, 0.0), m_v(n, 0.0), m_p(n, background_pressure()) {}

const std::vector<double>& WindData::u() const { return m_u; }

const std::vector<double>& WindData::v() const { return m_v; }

const std::vector<double>& WindData::p() const { return m_p; }

void WindData::setU(size_t index, double value){
  assert(index < m_u.size());
  m_u[index] = value;
}

void WindData::setV(size_t index, double value){
  assert(index < m_v.size());
  m_v[index] = value;
}

void WindData::setP(size_t index, double value){
  assert(index < m_p.size());
  m_p[index] = value;
}

size_t WindData::size() const { return m_n; }
