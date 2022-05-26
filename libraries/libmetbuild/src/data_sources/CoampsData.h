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
#ifndef METGET_SRC_COAMPSDATA_H_
#define METGET_SRC_COAMPSDATA_H_

#include <string>
#include <vector>

#include "CoampsDomain.h"
#include "GriddedData.h"

namespace MetBuild {

class CoampsData : public GriddedData {
 public:
  explicit CoampsData(std::vector<std::string> filenames);

  std::vector<std::vector<double>> latitude2d() override;
  const std::vector<double> &latitude1d() const override;

  std::vector<std::vector<double>> longitude2d() override;
  const std::vector<double> &longitude1d() const override;

  ~CoampsData() override = default;

  MetBuild::Triangulation generate_triangulation() const override;

 private:
  void initialize();

  void findCorners() override;

  void computeMasking();
  void computeCoordinates();

  std::vector<double> getArray1d(const std::string &variable) override;
  std::vector<std::vector<double>> getArray2d(
      const std::string &variable) override;

  std::vector<double> m_longitude;
  std::vector<double> m_latitude;
  std::vector<std::vector<double>> m_variables;
  std::vector<CoampsDomain> m_domains;
};
}  // namespace MetBuild
#endif  // METGET_SRC_COAMPSDATA_H_
