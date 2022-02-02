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
#include "Projection.h"

#include <cassert>
#include <string>
#include <tuple>

#include "Logging.h"
#include "proj.h"
#include "sqlite3.h"

using namespace MetBuild;

bool Projection::containsEpsg(int epsg) {
  projection_epsg_result result = {false, 0, ""};
  return Projection::queryProjDatabase(epsg, result) == 0;
}

std::string Projection::epsgDescription(int epsg) {
  projection_epsg_result result = {false, 0, ""};
  int ierr = Projection::queryProjDatabase(epsg, result);
  if (ierr == 0) {
    return std::get<2>(result);
  } else {
    return {};
  }
}

static int projection_sqlite_callback(void *data, int argc, char **argv,
                                      char **azColName) {
  (void)(azColName);  //...Silence warning, unused
  auto *v = static_cast<Projection::projection_epsg_result *>(data);
  if (argc < 1) {
    std::get<0>(*(v)) = false;
    return 1;
  }
  std::get<0>(*(v)) = true;
  std::get<1>(*(v)) = std::stoi(argv[1]);
  std::get<2>(*(v)) = argv[2];
  return 0;
}

int Projection::queryProjDatabase(int epsg, projection_epsg_result &result) {
  sqlite3 *db;
  sqlite3_open(proj_context_get_database_path(PJ_DEFAULT_CTX), &db);
  std::string queryString =
      "select distinct auth_name,code,name from crs_view where auth_name == "
      "'EPSG' and code == " +
      std::to_string(epsg) + ";";
  char *errString;
  sqlite3_exec(db, queryString.c_str(), projection_sqlite_callback, &result,
               &errString);
  sqlite3_close(db);
  if (std::get<0>(result)) return 0;
  return 1;
}

int Projection::transform(int epsgInput, int epsgOutput, double x, double y,
                          double &outx, double &outy, bool &isLatLon) {
  std::vector<double> xv = {x};
  std::vector<double> yv = {y};
  std::vector<double> outxv;
  std::vector<double> outyv;
  if (Projection::transform(epsgInput, epsgOutput, xv, yv, outxv, outyv,
                            isLatLon))
    return 1;
  outx = outxv[0];
  outy = outyv[0];
  return 0;
}

int Projection::transform(int epsgInput, int epsgOutput,
                          const std::vector<double> &x,
                          const std::vector<double> &y,
                          std::vector<double> &outx, std::vector<double> &outy,
                          bool &isLatLon) {
  isLatLon = false;
  if (x.size() != y.size()) return 1;
  if (x.empty()) return 2;

  if (!Projection::containsEpsg(epsgInput)) return 3;
  if (!Projection::containsEpsg(epsgOutput)) return 4;

  std::string p1 = "EPSG:" + std::to_string(epsgInput);
  std::string p2 = "EPSG:" + std::to_string(epsgOutput);
  PJ *pj1 =
      proj_create_crs_to_crs(PJ_DEFAULT_CTX, p1.c_str(), p2.c_str(), NULL);
  if (pj1 == nullptr) return 5;
  PJ *pj2 = proj_normalize_for_visualization(PJ_DEFAULT_CTX, pj1);
  if (pj2 == nullptr) return 6;
  proj_destroy(pj1);

  outx.clear();
  outy.clear();
  outx.reserve(x.size());
  outy.reserve(y.size());

  for (size_t i = 0; i < x.size(); ++i) {
    PJ_COORD cin;
    if (proj_angular_input(pj2, PJ_INV)) {
      cin.lp.lam = proj_torad(x[i]);
      cin.lp.phi = proj_torad(y[i]);
    } else {
      cin.xy.x = x[i];
      cin.xy.y = y[i];
    }

    PJ_COORD cout = proj_trans(pj2, PJ_FWD, cin);

    if (proj_angular_output(pj2, PJ_FWD)) {
      outx.push_back(proj_todeg(cout.lp.lam));
      outy.push_back(proj_todeg(cout.lp.phi));
      isLatLon = true;
    } else {
      outx.push_back(cout.xy.x);
      outy.push_back(cout.xy.y);
      isLatLon = false;
    }
  }
  proj_destroy(pj2);
  return 0;
}

std::vector<Point> Projection::transform(int epsgInput, int epsgOutput,
                                         const std::vector<Point> &points,
                                         bool &isLatLon) {
  assert(!points.empty());
  std::vector<Point> output;
  std::vector<double> x;
  std::vector<double> y;
  std::vector<double> xout;
  std::vector<double> yout;
  output.reserve(points.size());
  x.reserve(points.size());
  y.reserve(points.size());
  for (const auto &point : points) {
    x.push_back(point.x());
    y.push_back(point.y());
  }
  int ierr =
      Projection::transform(epsgInput, epsgOutput, x, y, xout, yout, isLatLon);
  if (ierr != 0) {
    metbuild_throw_exception(
        "Error while converting coordinates within proj. Code = " +
        std::to_string(ierr));
  }
  for (size_t i = 0; i < points.size(); ++i) {
    output.emplace_back(xout[i], yout[i]);
  }
  return output;
}

std::string Projection::projVersion() {
  return std::to_string(static_cast<unsigned long long>(PROJ_VERSION_MAJOR)) +
         "." +
         std::to_string(static_cast<unsigned long long>(PROJ_VERSION_MINOR)) +
         "." +
         std::to_string(static_cast<unsigned long long>(PROJ_VERSION_PATCH));
}

void Projection::setProjDatabaseLocation(const std::string &dblocation) {
  proj_context_set_database_path(PJ_DEFAULT_CTX, dblocation.c_str(), nullptr,
                                 nullptr);
}

std::string Projection::projDatabaseLocation() {
  return proj_context_get_database_path(PJ_DEFAULT_CTX);
}
