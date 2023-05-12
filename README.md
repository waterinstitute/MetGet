![MetGet Logo](https://raw.githubusercontent.com/waterinstitute/metget/main/img/MetGet_logo_blue.png)

MetGet is an application which allows users to query, format, and blend meteorological data from various sources
to be used in hydrodynamic modeling applications. The application is deployed using Kubernetes and
is configured to run as a set of services within the cluster acting as a RESTful API.

This project is in active development and should not be considered a production level product at this time.

## Development Partners

MetGet is developed by [The Water Institute](https://thewaterinstitute.org) and has been funded by the 
University of North Carolina at Chapel Hill [Coastal Resilience Center of Excellence](https://www.coastalresiliencecenter.org).

![The Water Institute](https://thewaterinstitute.org/images/01-Primary_Logo_Final.png)

![Coastal Resilience Center of Excellence](https://coastalresiliencecenter.unc.edu/wp-content/uploads/sites/845/2019/01/CoastalResilienceCenter-notexture-horiz-DHS-large.png)

![University of North Carolina at Chapel Hill](https://identity.unc.edu/wp-content/uploads/sites/885/2019/01/UNC_logo_webblue-e1517942350314.png)

## Recent Applications

MetGet has been utilized in forecasting applications, including those utilized during Hurricane Ian (2022)
where MetGet was able to supply multiple forecasting groups with meteorological data from the National Hurricane Center,
Global Forecast System, Hurricane Weather Research and Forecasting Model (HWRF), and COAMPS-TC model from the Naval Research
Laboratory in real time.

## Dependencies

MetGet is written in Python and C++ and utilizes the following applications/libraries:
- Argo
- AWS
- Postgres
- RabbitMQ
- Flask
- ecCodes
- netCDF4

## Usage

A client application is provided to interact with the MetGet services. The client application is a command line
interface (CLI) written in Python. The CLI is located in the `client` directory and can be run using the following
command:

```commandline
metget-client --help
```

The client application will use the following environment variables to connect to the MetGet services:

```bash
export METGET_ENDPOINT=https://api.metget.example.com
export METGET_API_KEY=abc123
export METGET_API_VERSION=1
```
Note that there are version 1 and version 2 APIs. Unless you are using a development version of MetGet, you should
use version 1. The default if the API version is not supplied will be version 1.
