#include "Grib.h"

#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <utility>

#include "Geometry.h"
#include "boost/format.hpp"
#include "eccodes.h"

using namespace MetBuild;

Grib::Grib(std::string filename)
    : m_filename(std::move(filename)),
      m_handle(nullptr),
      m_index(nullptr),
      m_tree(nullptr),
      m_ni(0),
      m_nj(0),
      m_size(0),
      m_convention(0) {
  initialize();
}

std::string Grib::filename() const { return m_filename; }

void Grib::initialize() {
  int ierr = 0;
  // size_t one = 1;
  codes_grib_multi_support_on(nullptr);
  m_index =
      codes_index_new_from_file(nullptr, &m_filename[0], "shortName", &ierr);
  if (ierr != 0) {
    throw std::runtime_error("Could not generate the eccodes index");
  }

  std::string var = "10u";
  CODES_CHECK(codes_index_select_string(m_index, "shortName", &var[0]),
              nullptr);

  m_handle = codes_handle_new_from_index(m_index, &ierr);

  CODES_CHECK(codes_get_long(m_handle, "Ni", &m_ni), nullptr);
  CODES_CHECK(codes_get_long(m_handle, "Nj", &m_nj), nullptr);
  CODES_CHECK(codes_get_size(m_handle, "values", &m_size), nullptr);

  this->readCoordinates();
  m_tree = std::make_unique<Kdtree>(m_longitude, m_latitude);

  this->findCorners();
}

Grib::~Grib() {
  if (m_handle) {
    codes_handle_delete(m_handle);
  }
  if (m_index) {
    codes_index_delete(m_index);
  }
}

std::vector<double> Grib::getGribArray1d(const std::string &name) {
  auto pvm = m_preread_value_map.find(name);
  if (pvm == m_preread_value_map.end()) {
    std::vector<double> arr1d(m_size);
    size_t s = m_size;
    int ierr = 0;
    std::string cname = name;
    CODES_CHECK(codes_index_select_string(m_index, "shortName", &cname[0]),
                nullptr);
    m_handle = codes_handle_new_from_index(m_index, &ierr);
    CODES_CHECK(codes_get_double_array(m_handle, "values", arr1d.data(), &s),
                nullptr);
    m_preread_values.push_back(arr1d);
    m_preread_value_map[name] = m_preread_values.size() - 1;
    return arr1d;
  } else {
    return m_preread_values[pvm->second];
  }
}

std::vector<std::vector<double>> Grib::getGribArray2d(const std::string &name) {
  return mapTo2d(this->getGribArray1d(name), ni(), nj());
}

std::vector<std::vector<double>> Grib::mapTo2d(const std::vector<double> &v,
                                               size_t ni, size_t nj) {
  std::vector<std::vector<double>> arr2d(ni);
  for (size_t i = 0; i < ni; ++i) {
    arr2d[i] = std::vector<double>(nj, 0.0);
  }

  for (size_t i = 0; i < v.size(); ++i) {
    arr2d[i / nj][i % nj] = v[i];
  }
  return arr2d;
}

const std::vector<double> &Grib::latitude1d() const { return m_latitude; }

const std::vector<double> &Grib::longitude1d() const { return m_longitude; }

std::vector<std::vector<double>> Grib::longitude2d() {
  return mapTo2d(this->m_longitude, ni(), nj());
}

std::vector<std::vector<double>> Grib::latitude2d() {
  return mapTo2d(this->m_latitude, ni(), nj());
}

const Kdtree *Grib::kdtree() const { return this->m_tree.get(); }

codes_handle *Grib::handle() const { return m_handle; }

size_t Grib::size() const { return m_size; }

long Grib::ni() const { return m_ni; }

long Grib::nj() const { return m_nj; }

void Grib::readCoordinates() {
  if (this->m_latitude.empty()) {
    m_latitude.resize(m_size);
    size_t s = m_size;
    CODES_CHECK(
        codes_get_double_array(m_handle, "latitudes", m_latitude.data(), &s),
        nullptr);
  }
  if (this->m_longitude.empty()) {
    m_longitude.resize(m_size);
    size_t s = m_size;
    CODES_CHECK(
        codes_get_double_array(m_handle, "longitudes", m_longitude.data(), &s),
        nullptr);
    if (m_convention == 0) {
      for (auto &v : m_longitude) {
        v = (std::fmod(v + 180.0, 360.0)) - 180.0;
      }
    }
  }
}

std::tuple<size_t, size_t> Grib::indexToPair(const size_t index) const {
  size_t j = index % nj();
  size_t i = index / nj();
  return std::make_pair(i, j);
}

bool Grib::point_inside(const Point &p) const {
  return this->m_geometry->is_inside(p);
}

void Grib::findCorners() {
  double xtl =
      *(std::min_element(m_longitude.begin(), m_longitude.begin() + m_ni - 1));
  double xtr =
      *(std::max_element(m_longitude.begin(), m_longitude.begin() + m_ni - 1));
  double xll = *(std::min_element(m_longitude.end() - m_ni, m_longitude.end()));
  double xlr = *(std::max_element(m_longitude.end() - m_ni, m_longitude.end()));

  double ytl =
      *(std::min_element(m_latitude.begin(), m_latitude.begin() + m_ni - 1));
  double ytr =
      *(std::max_element(m_latitude.begin(), m_latitude.begin() + m_ni - 1));
  double yll = *(std::min_element(m_latitude.end() - m_ni, m_latitude.end()));
  double ylr = *(std::max_element(m_latitude.end() - m_ni, m_latitude.end()));

  m_corners = {Point(xll, yll), Point(xlr, ylr), Point(xtr, ytr),
               Point(xtl, ytl)};
  m_geometry = std::make_unique<Geometry>(m_corners);
}
