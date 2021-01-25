
%module pymetbuild

%insert("python") %{
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
%}

%{
#define SWIG_FILE_WITH_INIT
#include "MetBuild_Global.h"
#include "Point.h"
#include "Meteorology.h"
#include "WindGrid.h"
#include "WindData.h"
#include "Kdtree.h"
#include "OwiAscii.h"
#include "OwiNetcdf.h"
#include "Date.h"
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
    %template(DoubleVector) vector<double>;
    %template(DoubleDoubleVector) vector<vector<double>>;
    %template(SizetSizetVector) vector<vector<size_t>>;
}

%include "MetBuild_Global.h"
%include "Point.h"
%include "Meteorology.h"
%include "WindGrid.h"
%include "WindData.h"
%include "Kdtree.h"
%include "OwiAscii.h"
%include "OwiNetcdf.h"
%include "Date.h"
