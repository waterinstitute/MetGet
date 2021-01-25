//
// Created by Zach Cobell on 9/7/20.
//

#include "NcFile.h"

#include <stdexcept>
#include <utility>

#include "netcdf.h"

NcFile::NcFile(std::string filename) : m_filename(std::move(filename)), m_ncid(0) {}

NcFile::~NcFile() {
  if (m_ncid != 0) {
    nc_close(m_ncid);
  }
}

void NcFile::ncCheck(const int err) {
  if (err != NC_NOERR) {
    throw std::runtime_error("Error from netCDF: " +
        std::string(nc_strerror(err)));
  }
}

int NcFile::ncid() const { return m_ncid; }

std::vector<NcFile::NcGroup>* NcFile::groups() { return &m_groups; }

void NcFile::initialize() {
  ncCheck(nc_create(m_filename.c_str(), NC_NETCDF4, &m_ncid));
}
