//
// Created by Zach Cobell on 9/7/20.
//

#ifndef METGET_SRC_NCFILE_H_
#define METGET_SRC_NCFILE_H_

#include <string>
#include <vector>

class NcFile {
 public:
  struct NcGroup {
    NcGroup()
        : grpid(0),
          dimid_time(0),
          dimid_xi(0),
          dimid_yi(0),
          varid_time(0),
          varid_lat(0),
          varid_lon(0),
          varid_press(0),
          varid_u(0),
          varid_v(0) {}
    int grpid;
    int dimid_time;
    int dimid_xi;
    int dimid_yi;
    int varid_time;
    int varid_lat;
    int varid_lon;
    int varid_press;
    int varid_u;
    int varid_v;
  };

  explicit NcFile(std::string filename);

  ~NcFile();

  int ncid() const;
  std::vector<NcFile::NcGroup> *groups();

  void initialize();

  static void ncCheck(int err);

 private:
  std::string m_filename;
  int m_ncid;
  std::vector<NcGroup> m_groups;
};

#endif  // METGET_SRC_NCFILE_H_
