#ifndef METGET_SRC_OWI_H_
#define METGET_SRC_OWI_H_

#include <string>
#include <vector>

#include "NcFile.h"

class OwiNetcdf {
 public:
  explicit OwiNetcdf(std::string filename);

  int initialize();

  void addGroup(const std::string &name, unsigned ni, unsigned nj, unsigned nt, bool movingGrid = false);

  void writeToFile(const std::string &filename);

 private:

  std::string m_filename;
  NcFile m_file;
};

#endif  // METGET_SRC_OWI_H_
