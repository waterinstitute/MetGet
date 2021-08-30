//
// Created by Zach Cobell on 1/23/21.
//

#ifndef METGET_LIBRARY_OWIASCII_H_
#define METGET_LIBRARY_OWIASCII_H_

#include <string>

#include "OwiAsciiDomain.h"
#include "WindGrid.h"
#include "WindData.h"

namespace MetBuild {

class OwiAscii {
 public:
  OwiAscii(const MetBuild::Date &date_start, const MetBuild::Date &date_end,
           unsigned time_step);

  int addDomain(const MetBuild::WindGrid &w, const std::string &pressureFile,
                const std::string &windFile);

  int write(const MetBuild::Date &date, const size_t domain_index,
            const WindData &data);

  int write(const MetBuild::Date &date, const size_t domain_index,
            const std::vector<std::vector<double>> &pressure,
            const std::vector<std::vector<double>> &wind_u,
            const std::vector<std::vector<double>> &wind_v);

 private:
  const Date m_startdate;
  const Date m_enddate;
  const unsigned m_timestep;
  std::vector<std::unique_ptr<OwiAsciiDomain>> m_domains;
};
}  // namespace MetBuild
#endif  // METGET_LIBRARY_OWIASCII_H_
