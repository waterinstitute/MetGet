//
// Created by Zach Cobell on 9/12/20.
//

#ifndef METGET_SRC_METTYPES_H_
#define METGET_SRC_METTYPES_H_

#include <string>

#include "boost/algorithm/string/case_conv.hpp"

namespace MetTypes {

enum eMetType { NONE, NAMANL, NAMFCST, GFSANL, GFSFCST, GFSNCEP, HWRF };

static eMetType stringToMetType(const std::string &s) {
  const std::string sup = boost::to_lower_copy(s);
  if (sup == "nam-analysis") return NAMANL;
  if (sup == "nam-forecast") return NAMFCST;
  if (sup == "gfs-analysis") return GFSANL;
  if (sup == "gfs-forecast") return GFSFCST;
  if (sup == "gfs-ncep") return GFSNCEP;
  if (sup == "hwrf") return HWRF;
  return NONE;
}
}  // namespace MetTypes

#endif  // METGET_SRC_METTYPES_H_
