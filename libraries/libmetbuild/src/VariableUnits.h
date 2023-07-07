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
#ifndef METGET_SRC_VARIABLEUNITS_H_
#define METGET_SRC_VARIABLEUNITS_H_

#include <utility>

#include "Logging.h"
#include "data_sources/GriddedDataTypes.h"

namespace MetBuild {

class VariableUnits {
 public:
  constexpr VariableUnits()
      : m_pressure(1.0),
        m_u10(1.0),
        m_v10(1.0),
        m_precipitation(1.0),
        m_humidity(1.0),
        m_temperature(1.0),
        m_ice(1.0) {}

  constexpr VariableUnits(double pressure_unit, double u10_unit,
                          double v10_unit, double precipitation_unit,
                          double humidity_unit, double temperature_unit,
                          double ice_unit)
      : m_pressure(pressure_unit),
        m_u10(u10_unit),
        m_v10(v10_unit),
        m_precipitation(precipitation_unit),
        m_humidity(humidity_unit),
        m_temperature(temperature_unit),
        m_ice(ice_unit){};

  constexpr double pressure() const { return m_pressure; }
  constexpr double u10() const { return m_u10; }
  constexpr double v10() const { return m_v10; }
  constexpr double temperature() const { return m_temperature; }
  constexpr double humidity() const { return m_humidity; }
  constexpr double ice() const { return m_ice; }
  constexpr double precipitation() const { return m_precipitation; }

  constexpr double find_variable(
      const MetBuild::GriddedDataTypes::VARIABLES &variable) const {
    switch (variable) {
      case GriddedDataTypes::VARIABLES::VAR_U10:
        return u10();
      case GriddedDataTypes::VARIABLES::VAR_V10:
        return v10();
      case GriddedDataTypes::VARIABLES::VAR_PRESSURE:
        return pressure();
      case GriddedDataTypes::VARIABLES::VAR_TEMPERATURE:
        return temperature();
      case GriddedDataTypes::VARIABLES::VAR_HUMIDITY:
        return humidity();
      case GriddedDataTypes::VARIABLES::VAR_ICE:
        return ice();
      case GriddedDataTypes::VARIABLES::VAR_RAINFALL:
        return precipitation();
      default:
        Logging::throwError("Invalid variable type specified");
        return 1.0;
    }
  }

 private:
  double m_pressure;
  double m_u10;
  double m_v10;
  double m_precipitation;
  double m_humidity;
  double m_temperature;
  double m_ice;
};

}  // namespace MetBuild

#endif  // METGET_SRC_VARIABLEUNITS_H_
