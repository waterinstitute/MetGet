![MetGet Logo](https://raw.githubusercontent.com/waterinstitute/metget/main/static/img/MetGet_logo_blue.png)
MetGet is an application which allows users to query, format, and blend meteorological data from various sources
to be used in hydrodynamic modeling applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/metget.svg)](https://badge.fury.io/py/metget)
![Testing](https://github.com/waterinstitute/metget/actions/workflows/pytest.yaml/badge.svg)
[![codecov](https://codecov.io/gh/waterinstitute/MetGet/branch/main/graph/badge.svg?token=I36RIBPFMD)](https://codecov.io/gh/waterinstitute/MetGet)

## Development Partners

MetGet is developed by [The Water Institute](https://thewaterinstitute.org) and has been funded by the 
University of North Carolina at Chapel Hill [Coastal Resilience Center of Excellence](https://www.coastalresiliencecenter.org).

![The Water Institute](https://thewaterinstitute.org/images/01-Primary_Logo_Final.png)

![Coastal Resilience Center of Excellence](https://coastalresiliencecenter.unc.edu/wp-content/uploads/sites/845/2019/01/CoastalResilienceCenter-notexture-horiz-DHS-large.png)

![University of North Carolina at Chapel Hill](https://identity.unc.edu/wp-content/uploads/sites/885/2019/01/UNC_logo_webblue-e1517942350314.png)

## MetGet Client Application
The MetGet client application is a tool that allows you to interact with the MetGet server. It may be used 
as a traditional command line tool or the `MetGetBuildRest` class may be imported and run in a custom application.

The MetGet client handles the interaction with the server via RESTful API calls and downloading output
data from S3 buckets. The client application is not a requirement for using MetGet, but it is a convenient
way to interact with the server.

## MetGet Server Access
The `metget` client application interacts with an instance of a [metget-server](https://github.com/waterinstitute/metget-server), 
which is a Kubernetes application that archives, builds, and provides to users meteorological data through the client application. 
The client does not require that you use any specific MetGet server instance. Instead, you may choose to operate your own 
`metget-server` instance or you may [contact](mailto:zcobell@thewaterinstitute.org) The Water Institute to request access to 
an available instance. 

### Installation

The MetGet client application can be installed using from the PyPi repository. The below commands show how to install the client and its dependencies.
```bash
$ pip3 install metget
```

### Terminology
There are several terms used in the MetGet client application that are important to understand. The below list of terms
aims to explain these terms and why they are available as options in the client application.

1. `analysis` - The term analysis is synonymous with the term "nowcast". It is the time when the model is initialized, or the "zero" hour of a model run. Requesting that MetGet provide "analysis" data via the `--analysis` command line option will fore MetGet to return only zero hour for any forecast runs. This option is incompatible with "--multiple-forecasts" and "--initialization-skip". 
2. `multiple-forecasts` - This option is used to signify that the user wants to request multiple forecast hours from the model. This allows MetGet to string together different forecasts to create quasi-hindcast data. The selection of available data is done by selecting unique times with the smallest offset from the start of their respective forecasts. This option is incompatible with `--analysis`.
3. `initialization-skip` - In some instances, it may be useful to skip the first [n] hours of a particular forecast when there is a potentially severe initialization that occurs in the atmospheric model. This option instructs MetGet to ignore the first [n] hours of a forecast. 

### Environment Variables
There are three influential environment variables which can be set as a convenience to the user. These variables are:
* `METGET_API_KEY` - The API key used to authenticate with MetGet
* `METGET_ENDPOINT` - The URL of the MetGet server, i.e. `https://metget.server.org`
* `METGET_API_VERSION` - The version of the MetGet API to use. The system will default to `1` and unless you are using the Kubernetes based MetGet deployment, the version 1 api is appropriate.

### Usage

The client application can request multiple types of data from the server. The below examples show how to request
data from a MetGet server instance via the command line tool.

Note: In the below examples, we assume that the above environment variables have been set. If they have not been set,
you will need to pass additional command line flags.

#### Example 1 - Request GFS data
This example requests data from the GFS for a two-day period. We will generate the data from a single self-consistent forecast
formatted as a single NetCDF file. The data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico.

```bash
$ metget build --domain gfs 0.25 -100 10 -80 30 \
               --start "2023-06-01 00:00" \
               --end "2023-06-03 00:00" \ 
               --timestep 3600 \ 
               --output metget_gfs_data.nc \
               --format generic-netcdf 
```

#### Example 2 - Request GFS data with multiple forecasts
This example requests data from the GFS for a thirty-day period. We will generate the data from multiple forecasts as a
quasi-hindcast. The data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico.

```bash
$ metget build --domain gfs 0.25 -100 10 -80 30 \
               --start "2023-05-01 00:00" \
               --end "2023-06-01 00:00" \ 
               --output metget_gfs_data.nc \
               --format generic-netcdf \
               --timestep 3600 \
               --multiple-forecasts
```

#### Example 3 - Request GFS data with multiple forecasts and initialization skip
This example requests data from the GFS for a thirty-day period. We will generate the data from multiple forecasts as a
quasi-hindcast. The data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico. We will
skip the first 6 hours of each forecast.

```bash
$ metget build --domain gfs 0.25 -100 10 -80 30 \
               --start "2023-05-01 00:00" \
               --end "2023-06-01 00:00" \ 
               --timestep 3600 \
               --format generic-netcdf \
               --multiple-forecasts \
               --initialization-skip 6 \
               --output metget_gfs_data.nc
```

#### Example 4 - Request HWRF data overlaid on GFS data
This example requests data from the HWRF model (Hurricane Mawar) with background forcing from the GFS model. Note that at the present time, 
the output format must support multi-domain data. Currently, the only format that supports this is `owi-ascii`. The
data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico.

```bash
$ metget build --domain hwrf-mawar02w 0.15 -90 20 -85 25 \
               --domain gfs 0.25 -100 10 -80 30 \
               --start "2023-06-01 00:00" \
               --end "2023-06-03 00:00" \ 
               --timestep 3600 \
               --backfill \
               --format owi-ascii \
               --output metget_hwrf_data
```

#### Example 5 - Get the status of the GFS model runs
This example demonstrates the ability for the system to provide information about what data is currently available

```bash
$ metget status gfs --format pretty
Status for model: GFS (class: synoptic)
+---------------------+---------------------+------------------+
|    Forecast Cycle   |       End Time      |      Status      |
+---------------------+---------------------+------------------+
| 2023-07-06 18:00:00 | 2023-07-17 09:00:00 | incomplete (255) |
| 2023-07-06 12:00:00 | 2023-07-22 12:00:00 |     complete     |
| 2023-07-06 06:00:00 | 2023-07-22 06:00:00 |     complete     |
| 2023-07-06 00:00:00 | 2023-07-22 00:00:00 |     complete     |
| 2023-07-05 18:00:00 | 2023-07-21 18:00:00 |     complete     |
| 2023-07-05 12:00:00 | 2023-07-21 12:00:00 |     complete     |
| 2023-07-05 06:00:00 | 2023-07-21 06:00:00 |     complete     |
| 2023-07-05 00:00:00 | 2023-07-21 00:00:00 |     complete     |
| 2023-07-04 18:00:00 | 2023-07-20 18:00:00 |     complete     |
| 2023-07-04 12:00:00 | 2023-07-20 12:00:00 |     complete     |
| 2023-07-04 06:00:00 | 2023-07-20 06:00:00 |     complete     |
| 2023-07-04 00:00:00 | 2023-07-20 00:00:00 |     complete     |
+---------------------+---------------------+------------------+
```

#### Example 6: Retrieve GEOJSON track data for a specific storm
This example demonstrates the ability to retrieve track data for a specific storm. The track data is returned in GEOJSON format.

```bash
$ metget track --year 2022 --storm 9 --basin al --type forecast --advisory 3 #...Hurricane Ian 2022, Advisory 3 track data
$ metget track --year 2022 --storm 9 --basin al --type besttrack #...Hurricane Ian 2022, best track data
```

### Custom Applications
The MetGet client library (`MetGetBuildRest`) can be imported and used in custom applications. The below example shows how to use the
client application in a custom Python script. Below is a simple version of how the main client application interacts with the `metget-client` library.
You can use this as a starting point for your own custom applications.

```python
import argparse
from metget_client.metget_build import MetGetBuildRest

metget_server = "https://metget.server.org"
metget_api_key = "my-api-key"
metget_api_version = 2

args = argparse.Namespace
output_format = 'owi-ascii'

# ...Building the request
request_data = MetGetBuildRest.generate_request_json(
    analysis=args.analysis,
    multiple_forecasts=args.multiple_forecasts,
    start_date=args.start,
    end_date=args.end,
    format=output_format,
    data_type=args.variable,
    backfill=args.backfill,
    time_step=args.timestep,
    domains=MetGetBuildRest.parse_command_line_domains(
        args.domain, args.initialization_skip
    ),
    compression=args.compression,
    epsg=args.epsg,
    filename=args.output,
    strict=args.strict,
    dry_run=args.dryrun,
    save_json_request=args.save_json_request,
)

client = MetGetBuildRest(metget_server, metget_api_key, metget_api_version)
data_id, status_code = client.make_metget_request(request_data)
client.download_metget_data(
    data_id,
    args.check_interval,
    args.max_wait,
)
```
