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
%module pymetbuild

%insert("python") %{
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
%}

%{
#define SWIG_FILE_WITH_INIT
#include "MetBuild_Global.h"
#include "CppAttributes.h"
#include "Point.h"
#include "Meteorology.h"
#include "Grid.h"
#include "data_sources/GriddedDataTypes.h"
#include "MeteorologicalData.h"
#include "Kdtree.h"
#include "Date.h"
#include "output/OutputFile.h"
#include "output/OwiAscii.h"
#include "output/OwiNetcdf.h"
#include "output/RasNetcdf.h"
#include "output/DelftOutput.h"
%}


%include <std_string.i>
%include <exception.i>
%include <std_vector.i>
%include <windows.i>

%exception {
  try {
    $action
  } catch (const std::exception& e) {
    SWIG_exception(SWIG_RuntimeError, e.what());
  } catch (const std::string& e) {
    SWIG_exception(SWIG_RuntimeError, e.c_str());
  }
}

namespace std {
    %template(IntVector) vector<int>;
    %template(SizetVector) vector<size_t>;
    %template(FloatVector) vector<float>;
    %template(DoubleVector) vector<double>;
    %template(DoubleDoubleVector) vector<vector<double>>;
    %template(SizetSizetVector) vector<vector<size_t>>;
    %template(StringVector) vector<string>;
}


%include "MetBuild_Global.h"
%include "Point.h"
%include "VariableNames.h"
%include "Meteorology.h"
%include "CppAttributes.h"
%include "Grid.h"
%include "data_sources/GriddedDataTypes.h"
%include "Kdtree.h"
%include "Date.h"
%include "MeteorologicalData.h"
%include "output/OutputFile.h"
%include "output/OwiAscii.h"
%include "output/OwiNetcdf.h"
%include "output/RasNetcdf.h"
%include "output/DelftOutput.h"

namespace MetBuild {
    %template(OneMetVector) MeteorologicalData<1,MeteorologicalDataType>;
    %template(TwoMetVector) MeteorologicalData<2,MeteorologicalDataType>;
    %template(ThreeMetVector) MeteorologicalData<3,MeteorologicalDataType>;
}
