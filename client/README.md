## MetGet client application
The MetGet client application is a tool that allows you to interact with the MetGet server. It may be used 
as a traditional command line tool or the `MetgetClient` class may be imported and run in a custom application.

The MetGet client handles the interaction with the server via RESTful API calls and downloading output
data from S3 buckets. The client application is not a requirement for using MetGet, but it is a convenient
way to interact with the server.

### Installation

The MetGet client application can be installed using `pip`. The below commands show how to install the client and its dependencies.
```bash
$ cd client
$ pip3 install .
```

### Terminology
There are several terms used in the MetGet client application that are important to understand. The below list of terms
aims to explain these terms and why they are available as options in the client application.

1. `analysis` - The term analysis is synonymous with the term "nowcast". It is the time when the model is initialized, or the "zero" hour of a model run. Requesting that MetGet provide "analysis" data via the `--analysis` command line option will fore MetGet to return only zero hour for any forecast runs. This option is incompatible with "--multiple-forecasts" and "--initialization-skip". 
2. `multiple-forecasts` - This option is used to signify that the user wants to request multiple forecast hours from the model. This allows MetGet to string together different forecasts to create quasi-hindcast data. The selection of available data is done by selecting unique times with the smallest offset from the start of their respective forecasts. This option is incompatible with `--analysis`.
3. `initialization-skip` - In some instances, it may be useful to skip the first [n] hours of a particular forecast when there is a potentially severe initialization that occurs in the atmospheric model. This option instructs MetGet to ignore the first [n] hours of a forecast. 

### Environment Variables
There are three influential environment variables which can be set as a convienience to the user. These variables are:
* `METGET_API_KEY` - The API key used to authenticate with MetGet
* `METGET_ENDPOINT` - The URL of the MetGet server, i.e. `https://api.metget.org`
* `METGET_API_VERSION` - The version of the MetGet API to use. The system will default to `1` and unless you are using the Kubernetes based MetGet deployment at `https://api.metget.org`, the version 1 api is appropriate. For the version at `https://api.metget.org`, this should be set to `2`.

### Usage

The client application can request multiple types of data from the server. The below examples show how to request
data from a MetGet server instance via the command line tool.

Note: In the below examples, we assume that the above environment variables have been set. If they have not been set,
you will need to pass additional command line flags.

#### Example 1 - Request GFS data
This example requests data from the GFS for a two-day period. We will generate the data from a single self-consistent forecast
formatted as a single NetCDF file. The data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico.

```bash
$ metget-client build --domain gfs 0.25 -100 10 -80 30 --start "2023-06-01 00:00" --end "2023-06-03 00:00" \ 
                --output metget_gfs_data.nc --format generic-netcdf --timestep 3600 
```

#### Example 2 - Request GFS data with multiple forecasts
This example requests data from the GFS for a thirty-day period. We will generate the data from multiple forecasts as a
quasi-hindcast. The data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico.

```bash
$ metget-client build --domain gfs 0.25 -100 10 -80 30 --start "2023-05-01 00:00" --end "2023-06-01 00:00" \ 
                --output metget_gfs_data.nc --format generic-netcdf --timestep 3600 --multiple-forecasts
```

#### Example 3 - Request GFS data with multiple forecasts and initialization skip
This example requests data from the GFS for a thirty-day period. We will generate the data from multiple forecasts as a
quasi-hindcast. The data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico. We will
skip the first 6 hours of each forecast.

```bash
$ metget-client build --domain gfs 0.25 -100 10 -80 30 --start "2023-05-01 00:00" --end "2023-06-01 00:00" \ 
                --output metget_gfs_data.nc --format generic-netcdf --timestep 3600 --multiple-forecasts --initialization-skip 6
```

#### Example 4 - Request HWRF data overlaid on GFS data
This example requests data from the HWRF model (Hurricane Mawar) with background forcing from the GFS model. Note that at the present time, 
the output format must support multi-domain data. Currently, the only format that supports this is `owi-ascii`. The
data will be interpolated to a 0.25 degree grid and cover a portion of the Gulf of Mexico.

```bash
$ metget-client build --domain hwrf-mawar02w 0.15 -90 20 -85 25 \
                      --domain gfs 0.25 -100 10 -80 30 \
                      --start "2023-06-01 00:00" --end "2023-06-03 00:00" \ 
                      --output metget_hwrf_data.ow --format owi-ascii \
                      --timestep 3600 --background gfs
```

### Custom Applications
The MetGet client library (`MetGetClient`) can be imported and used in custom applications. The below example shows how to use the
client application in a custom Python script. Below is a simple version of how the main client application interacts with the `metgetclient` library.
You can use this as a starting point for your own custom applications.

```python
from metgetclient.metget_build import MetGetBuildRest

metget_server = "https://api.metget.org"
metget_api_key = "my-api-key"
metget_api_version = 2

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
    domains=MetGetClient.parse_command_line_domains(
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