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
#define CATCH_CONFIG_MAIN

#include "MetBuild.h"
#include "catch.hpp"

TEST_CASE("Generate wind grid", "[Gen Wind Grid]") {
  double llx = -98.0;
  double lly = 10.0;
  double urx = -60.0;
  double ury = 40.0;
  double dx = 0.05;
  double dy = 0.05;
  auto wg = MetBuild::WindGrid(llx, lly, urx, ury, dx, dy);

  REQUIRE(wg.bottom_left().x() == llx);
  REQUIRE(wg.bottom_left().y() == lly);
  REQUIRE(wg.top_right().x() == urx);
  REQUIRE(wg.top_right().y() == ury);
  REQUIRE(wg.rotation() == 0.0);
  REQUIRE(wg.dx() == dx);
  REQUIRE(wg.dy() == dy);
  REQUIRE(wg.ni() == 761);
  REQUIRE(wg.nj() == 601);
  REQUIRE(wg.corner(10, 10).x() == -97.5);
  REQUIRE(wg.corner(10, 15).y() == 10.75);
  REQUIRE(wg.center(2, 5).x() == -97.85);
  REQUIRE(wg.center(5, 2).y() == 10.125);
}

TEST_CASE("Simple read", "[Simple read]") {
  double llx = -98.0;
  double lly = 10.0;
  double urx = -60.0;
  double ury = 40.0;
  double dx = 0.05;
  double dy = 0.05;

  auto wg = MetBuild::WindGrid(llx, lly, urx, ury, dx, dy);
  auto m = MetBuild::Meteorology(&wg);
  m.set_next_file("../testing/test_files/gfs.t00z.pgrb2.0p25.f000");
  m.set_next_file("../testing/test_files/gfs.t00z.pgrb2.0p25.f001");
  m.process_data();

  auto v = m.to_wind_grid();

  auto date_start = MetBuild::Date(2020, 1, 1, 0, 0, 0);
  auto date_end = MetBuild::Date(2020, 1, 2, 0, 0, 0);
  unsigned time_step = 900;

  auto owi = MetBuild::OwiAscii(date_start, date_end, time_step);
  owi.addDomain(wg, "fort.221", "fort.222");

  owi.write(date_start, 0, v.p(), v.u(), v.v());

  auto weight = MetBuild::Meteorology::generate_time_weight(
      date_start, date_end, date_start + time_step);
  v = m.to_wind_grid(weight);
  owi.write(date_start + time_step, 0, v.p(), v.u(), v.v());

  REQUIRE(0 == 0);
}
