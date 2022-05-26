
#include "MetBuild.h"

int main() {
    
    auto g = MetBuild::Grid(-100.0,10.0,-70.0,40.0,0.1,0.1);
    auto m = MetBuild::Meteorology(&g, MetBuild::Meteorology::COAMPS, MetBuild::GriddedDataTypes::WIND_PRESSURE);
    m.set_next_file({"../testing/test_files/coamps-tc_d01_2020082400_tau000.nc","../testing/test_files/coamps-tc_d02_2020082400_tau000.nc","../testing/test_files/coamps-tc_d03_2020082400_tau000.nc"});
    m.set_next_file({"../testing/test_files/coamps-tc_d01_2020082400_tau001.nc","../testing/test_files/coamps-tc_d02_2020082400_tau001.nc","../testing/test_files/coamps-tc_d03_2020082400_tau001.nc"});
    m.process_data();
    auto w = m.to_wind_grid(0.5);


    return 0;
}
