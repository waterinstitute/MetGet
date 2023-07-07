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
