//
// Created by Zach Cobell on 1/21/21.
//

#include "WindData.h"

using namespace MetBuild;

WindData::WindData(size_t n)
    : m_n(n), m_u(n, 0.0), m_v(n, 0.0), m_p(n, background_pressure()) {}

std::vector<double>& WindData::u() { return m_u; }

std::vector<double>& WindData::v() { return m_v; }

std::vector<double>& WindData::p() { return m_p; }

size_t WindData::size() const { return m_n; }
