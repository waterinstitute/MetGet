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
#ifndef METGET_SRC_VARIABLENAMES_H_
#define METGET_SRC_VARIABLENAMES_H_

#include <string>
#include <utility>

namespace MetBuild {

class VariableNames {
 public:
  VariableNames() = default;

  VariableNames(std::string longitude, std::string latitude,
                std::string pressure, std::string u10, std::string v10,
                std::string precipitation, std::string humidity,
                std::string temperature, std::string ice)
      : m_longitude(std::move(longitude)),
        m_latitude(std::move(latitude)),
        m_pressure(std::move(pressure)),
        m_u10(std::move(u10)),
        m_v10(std::move(v10)),
        m_precipitation(std::move(precipitation)),
        m_humidity(std::move(humidity)),
        m_temperature(std::move(temperature)),
        m_ice(std::move(ice)){};

  std::string longitude() const { return m_longitude; }
  std::string latitude() const { return m_latitude; }
  std::string pressure() const { return m_pressure; }
  std::string u10() const { return m_u10; }
  std::string v10() const { return m_v10; }
  std::string temperature() const { return m_temperature; }
  std::string humidity() const { return m_humidity; }
  std::string ice() const { return m_ice; }
  std::string precipitation() const { return m_precipitation; }

 private:
  std::string m_longitude;
  std::string m_latitude;
  std::string m_pressure;
  std::string m_u10;
  std::string m_v10;
  std::string m_precipitation;
  std::string m_humidity;
  std::string m_temperature;
  std::string m_ice;
};

}  // namespace MetBuild

#endif  // METGET_SRC_VARIABLENAMES_H_
