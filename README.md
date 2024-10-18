![MetGet Logo](https://raw.githubusercontent.com/waterinstitute/metget/main/static/img/MetGet_logo_blue.png)
MetGet is an application which allows users to query, format, and blend meteorological data from various sources
to be used in hydrodynamic modeling applications.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/metget.svg)](https://badge.fury.io/py/metget)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/metget.svg)](https://anaconda.org/conda-forge/metget)
[![Conda Platforms](https://img.shields.io/conda/pn/conda-forge/metget.svg)](https://anaconda.org/conda-forge/metget)
![Testing](https://github.com/waterinstitute/metget/actions/workflows/pytest.yaml/badge.svg)
[![codecov](https://codecov.io/gh/waterinstitute/MetGet/branch/main/graph/badge.svg?token=I36RIBPFMD)](https://codecov.io/gh/waterinstitute/MetGet)
[![Downloads](https://static.pepy.tech/badge/metget)](https://pepy.tech/project/metget)
![black](https://img.shields.io/badge/code%20style-black-000000.svg)

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

The MetGet client application can be installed using from the PyPi repository or via Anaconda using the
`conda-forge` repository. The below commands show how to install the client and its dependencies.

Using PyPi:
```bash
$ pip3 install metget
```

Using Anaconda:
```bash
$ conda install -c conda-forge metget
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
* `METGET_API_VERSION` - The version of the MetGet API to use. The system will default to `2`.

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

#### Example 7: Request the storm track data from the A-Deck
This example demonstrates how to get the storm track data for the GFS model (i.e. AVNO) for a specific storm
and cycle. The data is returned in tabular format, but optionally can be requested in a machine-readable json
format.
```bash
$ metget adeck --storm 14 --model AVNO --cycle 2024-10-08
+---------------------+-----------+----------+---------------+------------------+
|         Time        | Longitude | Latitude | Pressure (mb) | Wind Speed (mph) |
+---------------------+-----------+----------+---------------+------------------+
| 2024-10-08T00:00:00 |   -90.5   |   21.8   |      978      |      71.35       |
| 2024-10-08T06:00:00 |   -89.7   |   21.8   |      973      |      88.61       |
| 2024-10-08T12:00:00 |   -88.7   |   22.2   |      965      |      85.16       |
| 2024-10-08T18:00:00 |   -88.0   |   22.5   |      960      |      88.61       |
| 2024-10-09T00:00:00 |   -87.1   |   22.9   |      964      |      86.31       |
| 2024-10-09T06:00:00 |   -86.3   |   23.6   |      962      |      88.61       |
| 2024-10-09T12:00:00 |   -85.6   |   24.5   |      959      |      86.31       |
| 2024-10-09T18:00:00 |   -84.8   |   25.5   |      957      |      89.76       |
| 2024-10-10T00:00:00 |   -83.7   |   26.6   |      955      |      94.36       |
| 2024-10-10T06:00:00 |   -82.8   |   27.5   |      956      |      96.67       |
| 2024-10-10T12:00:00 |   -81.5   |   28.4   |      972      |      59.84       |
| 2024-10-10T18:00:00 |   -80.2   |   28.9   |      982      |      59.84       |
| 2024-10-11T00:00:00 |   -78.6   |   29.3   |      986      |       67.9       |
| 2024-10-11T06:00:00 |   -77.4   |   29.4   |      991      |       67.9       |
| 2024-10-11T12:00:00 |   -76.2   |   29.1   |      996      |      64.44       |
| 2024-10-11T18:00:00 |   -74.9   |   28.8   |      997      |      54.09       |
| 2024-10-12T00:00:00 |   -73.5   |   29.0   |      999      |      51.79       |
| 2024-10-12T06:00:00 |   -72.0   |   29.2   |      1000     |      43.73       |
| 2024-10-12T12:00:00 |   -70.5   |   29.7   |      1002     |      41.43       |
| 2024-10-12T18:00:00 |   -69.0   |   30.5   |      1003     |      44.88       |
| 2024-10-13T00:00:00 |   -67.0   |   31.3   |      1005     |      39.13       |
| 2024-10-13T06:00:00 |   -64.6   |   31.8   |      1006     |      32.22       |
| 2024-10-13T12:00:00 |   -62.0   |   32.2   |      1009     |      33.37       |
| 2024-10-13T18:00:00 |   -59.5   |   32.1   |      1009     |      31.07       |
| 2024-10-14T00:00:00 |   -57.2   |   32.3   |      1012     |      29.92       |
| 2024-10-14T06:00:00 |   -55.3   |   32.0   |      1012     |      27.62       |
| 2024-10-14T12:00:00 |   -54.9   |   30.9   |      1015     |      28.77       |
| 2024-10-14T18:00:00 |   -54.4   |   30.0   |      1014     |      27.62       |
| 2024-10-15T00:00:00 |   -54.0   |   29.5   |      1016     |      26.47       |
| 2024-10-15T06:00:00 |   -54.0   |   29.4   |      1014     |      23.02       |
| 2024-10-15T12:00:00 |   -53.9   |   29.7   |      1016     |      21.86       |
| 2024-10-15T18:00:00 |   -53.6   |   30.3   |      1013     |      21.86       |
| 2024-10-16T00:00:00 |   -53.0   |   31.4   |      1014     |      23.02       |
| 2024-10-16T06:00:00 |   -52.1   |   32.7   |      1012     |      21.86       |
| 2024-10-16T12:00:00 |   -50.9   |   34.5   |      1010     |      24.17       |
| 2024-10-16T18:00:00 |   -48.6   |   37.2   |      1007     |      33.37       |
| 2024-10-17T00:00:00 |   -45.1   |   40.3   |      1006     |      40.28       |
| 2024-10-17T06:00:00 |   -40.3   |   42.7   |      1004     |      46.03       |
| 2024-10-17T12:00:00 |   -36.2   |   44.4   |      1004     |      44.88       |
| 2024-10-17T18:00:00 |   -32.3   |   46.2   |      999      |      42.58       |
| 2024-10-18T00:00:00 |   -29.0   |   48.2   |      995      |      39.13       |
+---------------------+-----------+----------+---------------+------------------+
```

### Example 8: Request all active systems
This example demonstrates the ability to retrieve all active storms in the Atlantic basin. The data is returned in tabular format, but optionally can be requested in a machine-readable json format.
```bash
$ metget adeck --storm all --model AVNO --cycle 2024-10-08
+-------+-------------------+------------------+------------------------+---------------------------+
| Storm | Current Longitude | Current Latitude | Min Fcst Pressure (mb) | Max Fcst Wind Speed (mph) |
+-------+-------------------+------------------+------------------------+---------------------------+
|   13  |       -42.7       |       17.7       |          982           |           57.54           |
|   14  |       -90.5       |       21.8       |          955           |           96.67           |
+-------+-------------------+------------------+------------------------+---------------------------+
```

### Custom Applications
The MetGet client library (`MetGetBuildRest`) can be imported and used in custom applications. The below example shows how to use the
client application in a custom Python script. Below is a simple version of how the main client application interacts with the `metget-client` library.
You can use this as a starting point for your own custom applications.

```python
import argparse
from metget.metget_build import MetGetBuildRest

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
