Forcing Types
=============

The following is a summary of the types of forcing that are currently available through MetGet

Global Forecast System (GFS)
----------------------------
* Operator: NOAA NCEP
* MetGet Key: `gfs-ncep`
* Forecast Duration: 384 hours
* Time step: 0-120hr: 1hr; 121-384hr: 3hr
* Forecast Cycles: 00, 06, 12, 18
* `Source <https://www.nco.ncep.noaa.gov/pmb/products/gfs>`__

Description
^^^^^^^^^^^
The Global Forecast System (GFS) is a National Centers for Environmental Prediction (NCEP) weather forecast model that generates data for dozens of atmospheric and land-soil variables, including temperatures, winds, precipitation, soil moisture, and atmospheric ozone concentration. The system couples four separate models (atmosphere, ocean model, land/soil model, and sea ice) that work together to accurately depict weather conditions.


North American Mesoscale Model (NAM)
------------------------------------
* Operator: NOAA NCEP
* MetGet Key: `nam-ncep`
* Forecast Duration: 84 hours
* Time step: 0-36hr: 1hr; 37-84hr: 3hr
* Forecast Cycles: 00, 06, 12, 18
* `Source <https://www.nco.ncep.noaa.gov/pmb/products/nam/>`__

Description
^^^^^^^^^^^
The North American Mesoscale Forecast System (NAM) is one of the National Centers For Environmental Prediction’s (NCEP) major models for producing weather forecasts. NAM generates multiple grids (or domains) of weather forecasts over the North American continent at various horizontal resolutions. Each grid contains data for dozens of weather parameters, including temperature, precipitation, lightning, and turbulent kinetic energy. NAM uses additional numerical weather models to generate high-resolution forecasts over fixed regions, and occasionally to follow significant weather events like hurricanes.


Hurricane Weather Research and Forecasting (HWRF)
-------------------------------------------------
* Operator: NOAA NCEP
* MetGet Key: `hwrf`
* Forecast Duration: 126 hours
* Time step: 3hr
* Forecast Cycles: 00, 06, 12, 18
* `Source <https://nomads.ncep.noaa.gov/txt_descriptions/HWRF_doc.shtml>`__

Description
^^^^^^^^^^^
The HWRF model runs on-demand with input provided by the National Hurricane Center (NHC), Central Pacific Hurricane Center (CPHC), and/or Joint Typhoon Warning Center (JTWC). HWRF consists of multiple movable two-way interactive nested grids that follow the projected path of a tropical storm. The atmospheric component of the HWRF model was coupled to the Princeton Ocean Model (POM) for North Atlantic (NATL), Eastern Pacific (EPAC), and Central Pacific (CPAC) storms, and to the HYbrid Coordinate Ocean Model (HYCOM) for Western Pacific (WPAC), North Indian Ocean (NIO), and Southern hemisphere (SH) storms. Also, one-way coupling to wave model (Wave Watch III) was enabled for NATL, EPAC, and CPAC storms with hurricane surface wave products generated for these three basins. Grib filtering exists for the HWRF Wave Watch III data but it will only update when there are active tropical storms in these three basins.


