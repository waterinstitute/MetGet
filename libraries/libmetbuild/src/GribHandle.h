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
#ifndef METBUILD_SRC_GRIBHANDLE_H_
#define METBUILD_SRC_GRIBHANDLE_H_

#include <string>

#include "FileWrapper.h"
#include "Logging.h"
#include "boost/algorithm/string.hpp"

struct grib_handle;
typedef struct grib_handle codes_handle;

namespace MetBuild {

class GribHandle {
 public:
  GribHandle(const std::string &filename, const std::string &parameter,
             bool quiet = false);

  ~GribHandle();

  codes_handle *ptr();

 private:
  static void close_handle(grib_handle *ptr);

  static grib_handle *make_handle(const std::string &filename,
                                  const std::string &name, bool quiet);

  codes_handle *m_ptr;
};
}  // namespace MetBuild

#endif  // METBUILD_SRC_GRIBHANDLE_H_
