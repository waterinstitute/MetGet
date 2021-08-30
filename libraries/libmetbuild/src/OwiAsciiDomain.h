//
// Created by Zach Cobell on 1/23/21.
//

#ifndef METGET_LIBRARY_OWIASCIIDOMAIN_H_
#define METGET_LIBRARY_OWIASCIIDOMAIN_H_

#include <fstream>
#include <memory>
#include <string>
#include <vector>

#include "Date.h"
#include "WindGrid.h"

namespace MetBuild {

class OwiAsciiDomain {
 public:
  OwiAsciiDomain(const MetBuild::WindGrid *grid,
                 const MetBuild::Date &startDate, const MetBuild::Date &endDate,
                 unsigned time_step, std::string pressureFile,
                 std::string windFile);

  ~OwiAsciiDomain();

  int write(const MetBuild::Date &date, 
            const std::vector<std::vector<double>> &pressure,
            const std::vector<std::vector<double>> &wind_u,
            const std::vector<std::vector<double>> &wind_v);

  void open();

  void close();

 private:
  void write_header();

  static std::string generateHeaderLine(const Date &date1, const Date &date2);
  static std::string generateRecordHeader(const Date &date,
                                          const WindGrid *grid);
  void write_record(std::ofstream *stream,
                           const std::vector<std::vector<double>> &value) const;

  bool m_isOpen;
  const Date m_startDate;
  const Date m_endDate;
  Date m_previousDate;
  const unsigned m_timestep;
  std::unique_ptr<std::ofstream> m_ofstream_pressure;
  std::unique_ptr<std::ofstream> m_ofstream_wind;
  const WindGrid *m_windGrid;
  const std::string m_pressureFile;
  const std::string m_windFile;
};
}  // namespace MetBuild

#endif  // METGET_LIBRARY_OWIASCIIDOMAIN_H_
