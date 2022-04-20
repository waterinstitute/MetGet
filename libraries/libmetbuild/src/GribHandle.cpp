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
#include "GribHandle.h"

#include "Utilities.h"
#include "eccodes.h"

using namespace MetBuild;

GribHandle::GribHandle(const std::string &filename,
                       const std::string &parameter, bool quiet)
    : m_ptr(make_handle(filename, parameter, quiet)) {}

GribHandle::~GribHandle() { close_handle(m_ptr); }

codes_handle *GribHandle::ptr() { return m_ptr; }

void GribHandle::close_handle(grib_handle *ptr) {
  auto err = codes_handle_delete(ptr);
  if (err != GRIB_SUCCESS) {
    metbuild_throw_exception(
        "Could not delete the codes_handle object. Possible memory leak.");
  }
}

grib_handle *GribHandle::make_handle(const std::string &filename,
                                     const std::string &name, bool quiet) {
  auto f = FileWrapper(filename, "r");
  int ierr = 0;

  while (auto h = codes_handle_new_from_file(codes_context_get_default(),
                                             f.ptr(), PRODUCT_GRIB, &ierr)) {
    CODES_CHECK(ierr, nullptr);
    std::string pname;
    std::string p2name;
    size_t plen = 0;
    CODES_CHECK(codes_get_length(h, "shortName", &plen), nullptr);
    pname.resize(plen, ' ');
    CODES_CHECK(codes_get_string(h, "shortName", &pname[0], &plen), nullptr);
    boost::trim_if(pname, Utilities::isNotAlpha);
    if (pname == name) {
      return h;
    } else {
      close_handle(h);
    }
  }
  if (!quiet) metbuild_throw_exception("Could not generate the eccodes handle");
  return nullptr;
}