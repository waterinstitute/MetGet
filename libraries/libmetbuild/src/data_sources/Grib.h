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
#ifndef METBUILD_GRIB_H
#define METBUILD_GRIB_H

#include <array>
#include <cstdlib>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

#include "GriddedData.h"
#include "Kdtree.h"
#include "Point.h"
#include "VariableNames.h"

//...Forward Declarations
struct grib_handle;
struct grib_index;
typedef struct grib_handle codes_handle;
typedef struct grib_index codes_index;
typedef struct grib_context codes_context;

namespace MetBuild {

class Grib : public GriddedData {
 public:
  explicit Grib(std::string filename, VariableNames variable_names);

  ~Grib();

  NODISCARD std::vector<std::vector<double>> latitude2d() override;
  NODISCARD const std::vector<double> &latitude1d() const override;

  NODISCARD std::vector<std::vector<double>> longitude2d() override;
  NODISCARD const std::vector<double> &longitude1d() const override;

  void write_to_ascii(const std::string &filename, const std::string &varname);

  static bool containsVariable(const std::string &filename,
                               const std::string &variableName);

  static int getStepLength(const std::string &filename,
                           const std::string &parameter);

 private:
  void initialize();

  void findCorners() override;

  std::vector<double> getArray1d(const std::string &name) override;
  std::vector<std::vector<double>> getArray2d(const std::string &name) override;

  void readCoordinates(codes_handle *handle);
  static std::vector<std::vector<double>> mapTo2d(const std::vector<double> &v,
                                                  size_t ni, size_t nj);

  std::vector<double> m_latitude;
  std::vector<double> m_longitude;
  std::vector<std::vector<double>> m_preread_values;
  std::unordered_map<std::string, size_t> m_preread_value_map;
  std::unique_ptr<FILE *> m_file;
  int m_convention;
};
}  // namespace MetBuild
#endif  // METBUILD_GRIB_H
