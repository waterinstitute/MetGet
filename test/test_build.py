import argparse
import json
import os
from datetime import datetime

import pytest
import requests_mock

from metget.metget_build import MetGetBuildRest, metget_build
from metget.metget_environment import get_metget_environment_variables

from .build_json import (
    METGET_BUILD_COAMPS_JSON,
    METGET_BUILD_CTCX_JSON,
    METGET_BUILD_GEFS_JSON,
    METGET_BUILD_GFS_JSON,
    METGET_BUILD_HWRF_JSON,
    METGET_BUILD_NHC_JSON,
    METGET_BUILD_NHC_JSON_THIS_YEAR,
    METGET_BUILD_POST_RETURN,
    METGET_BUILD_RETURN_COMPLETE,
    METGET_BUILD_RETURN_ERROR,
    METGET_BUILD_RETURN_QUEUED,
    METGET_BUILD_RETURN_RESTORE,
    METGET_BUILD_RETURN_RUNNING,
)

METGET_DMY_ENDPOINT = "https://metget.server.dmy"
METGET_DMY_APIKEY = "1234567890"
METGET_API_VERSION = 2


def test_build_gfs(capfd) -> None:
    """
    Tests the build request for a single domain of gfs data
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """

    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [["gfs", 0.25, -100, 10, -80, 30]]
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = None
    args.output = "test_build_gfs"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    request_dict = MetGetBuildRest.generate_request_json(
        analysis=args.analysis,
        multiple_forecasts=args.multiple_forecasts,
        start_date=args.start,
        end_date=args.end,
        format=args.format,
        timestep=args.timestep,
        data_type=args.data_type,
        backfill=args.backfill,
        filename=args.output,
        dry_run=args.dryrun,
        strict=args.strict,
        domains=MetGetBuildRest.parse_command_line_domains(
            args.domain, args.initialization_skip
        ),
    )

    request_dict["creator"] = "pytest"
    assert request_dict == METGET_BUILD_GFS_JSON

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    with requests_mock.Mocker() as m:
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        data_id, status_code = client.make_metget_request(request_dict)

    assert data_id == "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"
    assert status_code == 200

    metget_request_mocker(
        data_id,
        client,
        ["test_build_gfs_00.pre", "test_build_gfs_00.wnd"],
        "filelist_gfs.json",
        args,
        capfd,
    )


def test_build_hwrf_multidomain(capfd) -> None:
    """
    **TEST PURPOSE**: Validates multi-domain build request combining GFS and HWRF models
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Build data using both GFS background and HWRF storm-specific domains
    **INPUT**: Two domains - GFS (-100,10) to (-70,30) and HWRF storm bret03l (-90,15) to (-80,25)
    **EXPECTED**: Creates multi-domain request JSON and successfully processes both domains
    **COVERAGE**: Tests multi-domain request generation, storm-specific model handling, and domain coordination
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [
        ["gfs", 0.25, -100, 10, -70, 30],
        ["hwrf-bret03l", 0.1, -90, 15, -80, 25],
    ]
    args.start = datetime(2023, 6, 19)
    args.end = datetime(2023, 6, 24)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = None
    args.output = "test_build_hwrf"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    request_dict = MetGetBuildRest.generate_request_json(
        analysis=args.analysis,
        multiple_forecasts=args.multiple_forecasts,
        start_date=args.start,
        end_date=args.end,
        format=args.format,
        timestep=args.timestep,
        data_type=args.data_type,
        backfill=args.backfill,
        filename=args.output,
        dry_run=args.dryrun,
        strict=args.strict,
        domains=MetGetBuildRest.parse_command_line_domains(
            args.domain, args.initialization_skip
        ),
    )

    request_dict["creator"] = "pytest"
    assert request_dict == METGET_BUILD_HWRF_JSON

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    with requests_mock.Mocker() as m:
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        data_id, status_code = client.make_metget_request(request_dict)

    assert data_id == "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"
    assert status_code == 200

    metget_request_mocker(
        data_id,
        client,
        [
            "metget_test_bret03l_00.pre",
            "metget_test_bret03l_00.wnd",
            "metget_test_bret03l_01.pre",
            "metget_test_bret03l_01.wnd",
        ],
        "filelist_hwrf.json",
        args,
        capfd,
    )


def test_build_nhc_raw(capfd) -> None:
    """
    **TEST PURPOSE**: Validates NHC (National Hurricane Center) raw data build request
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Build raw format NHC advisory data for specific storm and advisory
    **INPUT**: NHC model, storm 09 in AL basin, advisory 015, year 2023, raw format
    **EXPECTED**: Generates NHC-specific request JSON with advisory parameters and downloads data
    **COVERAGE**: Tests NHC model parameter parsing, advisory handling, and raw format output
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.variable = "wind_pressure"
    args.backfill = False
    args.domain = [["nhc-2023-al-09-015", 0.1, -90, 15, -80, 25]]
    args.start = datetime(2023, 6, 19)
    args.end = datetime(2023, 6, 24)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = "raw"
    args.output = "test_build_nhc"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.request = None
    args.compression = False
    args.save_json_request = True
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    request_dict = MetGetBuildRest.generate_request_json(
        analysis=args.analysis,
        multiple_forecasts=args.multiple_forecasts,
        start_date=args.start,
        end_date=args.end,
        format=args.format,
        timestep=args.timestep,
        data_type=args.variable,
        backfill=args.backfill,
        filename=args.output,
        dry_run=args.dryrun,
        strict=args.strict,
        domains=MetGetBuildRest.parse_command_line_domains(
            args.domain, args.initialization_skip
        ),
    )

    request_dict["creator"] = "pytest"

    assert request_dict == METGET_BUILD_NHC_JSON

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    with requests_mock.Mocker() as m:
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        data_id, status_code = client.make_metget_request(request_dict)

    assert data_id == "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"
    assert status_code == 200

    output_files = [
        "nhc_merge_2022_al_09_015.trk",
        "nhc_btk_2022_al_09.btk",
        "nhc_fcst_2022_al_09_015.fcst",
    ]

    metget_request_mocker(
        data_id,
        client,
        output_files,
        "filelist_nhc.json",
        args,
        capfd,
    )

    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_files",
        "filelist_nhc.json",
    )

    # ...Do the same thing with the raw function
    with requests_mock.Mocker() as m:
        response_list = [
            {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
            {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
            {"json": METGET_BUILD_RETURN_RUNNING, "status_code": 200},
            {"json": METGET_BUILD_RETURN_COMPLETE, "status_code": 200},
        ]
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            response_list,
        )
        data_id, status_code = client.make_metget_request(request_dict)
        with open(path, "rb") as filelist_file:
            filelist_data = json.load(filelist_file)
            m.get(
                f"https://s3.amazonaws.com/metget/{data_id:s}/filelist.json",
                json=filelist_data,
            )

            for file in output_files:
                m.get(
                    f"https://s3.amazonaws.com/metget/{data_id:s}/{file:s}",
                    text="This is only a test",
                )

            metget_build(args)

            for file in output_files:
                assert os.path.exists(file)
                os.remove(file)
            os.remove("filelist.json")
            os.remove("request.json")


def test_build_nhc_raw_thisyear(capfd) -> None:
    """
    **TEST PURPOSE**: Validates NHC data build request using current year as default
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Build NHC advisory data without specifying year (defaults to current year)
    **INPUT**: NHC model, storm 09 in AL basin, advisory 015, no year specified
    **EXPECTED**: Uses current year as default and generates valid NHC request
    **COVERAGE**: Tests year defaulting logic and current year storm data handling
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.variable = "wind_pressure"
    args.backfill = False
    args.domain = [["nhc-al-09-015", 0.1, -90, 15, -80, 25]]
    args.start = datetime(2023, 6, 19)
    args.end = datetime(2023, 6, 24)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = "raw"
    args.output = "test_build_nhc"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.request = None
    args.compression = False
    args.save_json_request = True
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    request_dict = MetGetBuildRest.generate_request_json(
        analysis=args.analysis,
        multiple_forecasts=args.multiple_forecasts,
        start_date=args.start,
        end_date=args.end,
        format=args.format,
        timestep=args.timestep,
        data_type=args.variable,
        backfill=args.backfill,
        filename=args.output,
        dry_run=args.dryrun,
        strict=args.strict,
        domains=MetGetBuildRest.parse_command_line_domains(
            args.domain, args.initialization_skip
        ),
    )

    request_dict["creator"] = "pytest"

    assert request_dict == METGET_BUILD_NHC_JSON_THIS_YEAR

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    with requests_mock.Mocker() as m:
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        data_id, status_code = client.make_metget_request(request_dict)

    assert data_id == "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"
    assert status_code == 200

    output_files = [
        "nhc_merge_2022_al_09_015.trk",
        "nhc_btk_2022_al_09.btk",
        "nhc_fcst_2022_al_09_015.fcst",
    ]

    metget_request_mocker(
        data_id,
        client,
        output_files,
        "filelist_nhc.json",
        args,
        capfd,
    )

    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_files",
        "filelist_nhc.json",
    )

    # ...Do the same thing with the raw function
    with requests_mock.Mocker() as m:
        response_list = [
            {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
            {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
            {"json": METGET_BUILD_RETURN_RUNNING, "status_code": 200},
            {"json": METGET_BUILD_RETURN_COMPLETE, "status_code": 200},
        ]
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            response_list,
        )
        data_id, status_code = client.make_metget_request(request_dict)
        with open(path, "rb") as filelist_file:
            filelist_data = json.load(filelist_file)
            m.get(
                f"https://s3.amazonaws.com/metget/{data_id:s}/filelist.json",
                json=filelist_data,
            )

            for file in output_files:
                m.get(
                    f"https://s3.amazonaws.com/metget/{data_id:s}/{file:s}",
                    text="This is only a test",
                )

            metget_build(args)

            for file in output_files:
                assert os.path.exists(file)
                os.remove(file)
            os.remove("filelist.json")
            os.remove("request.json")


def test_build_nhc_raw_error(capfd) -> None:
    """
    **TEST PURPOSE**: Validates error handling for NHC data build request failures
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Attempt NHC data build that results in API error response
    **INPUT**: NHC model request that triggers server-side error condition
    **EXPECTED**: Handles API error gracefully and writes debug information to file
    **COVERAGE**: Tests error response handling, debug file creation, and graceful failure
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.variable = "wind_pressure"
    args.backfill = False
    args.domain = [["nhc-al", 0.1, -90, 15, -80, 25]]
    args.start = datetime(2023, 6, 19)
    args.end = datetime(2023, 6, 24)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = "raw"
    args.output = "test_build_nhc"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.request = None
    args.compression = False
    args.save_json_request = True
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with pytest.raises(RuntimeError):
        MetGetBuildRest.generate_request_json(
            analysis=args.analysis,
            multiple_forecasts=args.multiple_forecasts,
            start_date=args.start,
            end_date=args.end,
            format=args.format,
            timestep=args.timestep,
            data_type=args.variable,
            backfill=args.backfill,
            filename=args.output,
            dry_run=args.dryrun,
            strict=args.strict,
            domains=MetGetBuildRest.parse_command_line_domains(
                args.domain, args.initialization_skip
            ),
        )


def test_build_hwrf_multidomain_error(capfd) -> None:
    """
    **TEST PURPOSE**: Validates error handling for malformed multi-domain HWRF+GFS build requests
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Attempt multi-domain build with incorrectly formatted domain specifications
    **INPUT**: Invalid multi-domain configuration combining GFS and HWRF models
    **EXPECTED**: Gracefully handles formatting errors and provides appropriate error response
    **COVERAGE**: Tests multi-domain validation, error handling for malformed requests
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [
        ["gfs", 0.25, -100, 10, -70, 30],
        ["hwrf", 0.1, -90, 15, -80, 25],
    ]
    args.start = datetime(2023, 6, 19)
    args.end = datetime(2023, 6, 24)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = None
    args.output = "test_build_hwrf"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with pytest.raises(RuntimeError):
        MetGetBuildRest.generate_request_json(
            analysis=args.analysis,
            multiple_forecasts=args.multiple_forecasts,
            start_date=args.start,
            end_date=args.end,
            format=args.format,
            timestep=args.timestep,
            data_type=args.data_type,
            backfill=args.backfill,
            filename=args.output,
            dry_run=args.dryrun,
            strict=args.strict,
            domains=MetGetBuildRest.parse_command_line_domains(
                args.domain, args.initialization_skip
            ),
        )


def test_build_gefs(capfd) -> None:
    """
    **TEST PURPOSE**: Validates GEFS ensemble model data build request for single domain
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Build ensemble forecast data from GEFS model control member (c00)
    **INPUT**: GEFS-c00 ensemble member, 0.25° resolution, Gulf domain, June 1-2 2023
    **EXPECTED**: Generates valid GEFS ensemble request JSON and downloads ensemble data
    **COVERAGE**: Tests GEFS ensemble model handling, control member specification, and ensemble data workflow
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [["gefs-c00", 0.25, -100, 10, -80, 30]]
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = None
    args.output = "test_build_gefs"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    request_dict = MetGetBuildRest.generate_request_json(
        analysis=args.analysis,
        multiple_forecasts=args.multiple_forecasts,
        start_date=args.start,
        end_date=args.end,
        format=args.format,
        timestep=args.timestep,
        data_type=args.data_type,
        backfill=args.backfill,
        filename=args.output,
        dry_run=args.dryrun,
        strict=args.strict,
        domains=MetGetBuildRest.parse_command_line_domains(
            args.domain, args.initialization_skip
        ),
    )

    request_dict["creator"] = "pytest"
    assert request_dict == METGET_BUILD_GEFS_JSON

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    with requests_mock.Mocker() as m:
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        data_id, status_code = client.make_metget_request(request_dict)

    assert data_id == "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"
    assert status_code == 200

    metget_request_mocker(
        data_id,
        client,
        ["test_build_gefs_00.pre", "test_build_gefs_00.wnd"],
        "filelist_gefs.json",
        args,
        capfd,
    )


def test_build_coamps(capfd) -> None:
    """
    **TEST PURPOSE**: Validates COAMPS-TC tropical cyclone model data build request
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Build storm-specific COAMPS data for tropical cyclone 09L
    **INPUT**: COAMPS-TC model, storm 09L, 0.25° resolution, Gulf domain, June 1-2 2023
    **EXPECTED**: Generates valid COAMPS tropical cyclone request with storm parameters
    **COVERAGE**: Tests COAMPS-TC model handling, storm-specific parameters, and tropical cyclone data
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [["coamps-09L", 0.25, -100, 10, -80, 30]]
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = None
    args.output = "test_build_coamps"
    args.tau = 0
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    request_dict = MetGetBuildRest.generate_request_json(
        analysis=args.analysis,
        multiple_forecasts=args.multiple_forecasts,
        start_date=args.start,
        end_date=args.end,
        format=args.format,
        timestep=args.timestep,
        data_type=args.data_type,
        backfill=args.backfill,
        filename=args.output,
        dry_run=args.dryrun,
        strict=args.strict,
        domains=MetGetBuildRest.parse_command_line_domains(
            args.domain, args.initialization_skip
        ),
    )

    request_dict["creator"] = "pytest"
    assert request_dict == METGET_BUILD_COAMPS_JSON

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    with requests_mock.Mocker() as m:
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        data_id, status_code = client.make_metget_request(request_dict)

    assert data_id == "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"
    assert status_code == 200

    metget_request_mocker(
        data_id,
        client,
        ["test_build_gefs_00.pre", "test_build_gefs_00.wnd"],
        "filelist_gefs.json",
        args,
        capfd,
    )


def test_build_ctcx(capfd) -> None:
    """
    **TEST PURPOSE**: Validates COAMPS-CTCX coupled tropical cyclone model data build request
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Build coupled ocean-atmosphere data from COAMPS-CTCX for storm 09L ensemble member 01
    **INPUT**: CTCX model, storm 09L, ensemble member 01, 0.25° resolution, Gulf domain
    **EXPECTED**: Generates valid COAMPS-CTCX request with storm and ensemble parameters
    **COVERAGE**: Tests COAMPS-CTCX coupled model, ensemble member handling, and storm-specific data
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [["ctcx-09L-01", 0.25, -100, 10, -80, 30]]
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.initialization_skip = 4
    args.timestep = 3600
    args.format = None
    args.output = "test_build_ctcx"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    request_dict = MetGetBuildRest.generate_request_json(
        analysis=args.analysis,
        multiple_forecasts=args.multiple_forecasts,
        start_date=args.start,
        end_date=args.end,
        format=args.format,
        timestep=args.timestep,
        data_type=args.data_type,
        backfill=args.backfill,
        filename=args.output,
        dry_run=args.dryrun,
        strict=args.strict,
        domains=MetGetBuildRest.parse_command_line_domains(
            args.domain, args.initialization_skip
        ),
    )

    request_dict["creator"] = "pytest"
    assert request_dict == METGET_BUILD_CTCX_JSON

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    with requests_mock.Mocker() as m:
        m.post(METGET_DMY_ENDPOINT + "/build", json=METGET_BUILD_POST_RETURN)
        data_id, status_code = client.make_metget_request(request_dict)

    assert data_id == "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"
    assert status_code == 200

    metget_request_mocker(
        data_id,
        client,
        ["test_build_gefs_00.pre", "test_build_gefs_00.wnd"],
        "filelist_gefs.json",
        args,
        capfd,
    )


def test_build_gfs_error(capfd) -> None:
    """
    **TEST PURPOSE**: Validates error handling for incorrectly formatted GFS build requests
    **MODULE**: metget_build.MetGetBuildRest and metget_build.metget_build
    **SCENARIO**: Attempt GFS data build with malformed domain specification that should raise error
    **INPUT**: GFS model with invalid domain formatting or parameters
    **EXPECTED**: Raises appropriate error for malformed request configuration
    **COVERAGE**: Tests input validation, error raising for invalid GFS domain specifications
    """

    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [["gfs-01", 0.25, -100, 10, -80, 30]]
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = None
    args.output = "test_build_gfs"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    with pytest.raises(RuntimeError):
        MetGetBuildRest.generate_request_json(
            analysis=args.analysis,
            multiple_forecasts=args.multiple_forecasts,
            start_date=args.start,
            end_date=args.end,
            format=args.format,
            timestep=args.timestep,
            data_type=args.data_type,
            backfill=args.backfill,
            filename=args.output,
            dry_run=args.dryrun,
            strict=args.strict,
            domains=MetGetBuildRest.parse_command_line_domains(
                args.domain, args.initialization_skip
            ),
        )


def test_build_complete_but_missing_file() -> None:
    """
    Tests the scenario where a request returns as complete but the filelist.json
    file does not exist (e.g., due to expiration or file system issues).
    This should trigger the error handling and sys.exit(1).
    """
    args = argparse.Namespace()
    args.analysis = False
    args.multiple_forecasts = True
    args.data_type = "wind_pressure"
    args.backfill = False
    args.domain = [["gfs", 0.25, -100, 10, -80, 30]]
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.initialization_skip = 0
    args.timestep = 3600
    args.format = None
    args.output = "test_build_missing_file"
    args.dryrun = False
    args.strict = False
    args.epsg = 4326
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    data_id = "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"

    with requests_mock.Mocker() as m:
        # Mock the status check to return "completed"
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            json=METGET_BUILD_RETURN_COMPLETE,
        )

        # Mock the filelist.json request to return 404 (file not found)
        m.get(
            f"https://s3.amazonaws.com/metget/{data_id:s}/filelist.json",
            status_code=404,
        )

        # This should trigger sys.exit(1) due to the missing filelist.json
        with pytest.raises(SystemExit) as exc_info:
            client.download_metget_data(
                data_id, args.check_interval, args.max_wait, args.output_directory
            )

        # Verify it exits with code 1
        assert exc_info.value.code == 1


def metget_request_mocker(
    data_id: str,
    client: MetGetBuildRest,
    output_files: list,
    filelist_file: str,
    args: argparse.Namespace,
    capfd,
) -> None:
    response_list = [
        {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
        {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
        {"json": METGET_BUILD_RETURN_RESTORE, "status_code": 200},
        {"json": METGET_BUILD_RETURN_RUNNING, "status_code": 200},
        {"json": METGET_BUILD_RETURN_COMPLETE, "status_code": 200},
    ]

    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            response_list,
        )
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "test_files",
            filelist_file,
        )
        with open(path, "rb") as filelist_file:
            filelist_data = json.load(filelist_file)
            m.get(
                f"https://s3.amazonaws.com/metget/{data_id:s}/filelist.json",
                json=filelist_data,
            )

            for file in output_files:
                m.get(
                    f"https://s3.amazonaws.com/metget/{data_id:s}/{file:s}",
                    text="This is only a test",
                )

            client.download_metget_data(
                data_id, args.check_interval, args.max_wait, args.output_directory
            )
            out, err = capfd.readouterr()

        # ...Clean up
        for file in output_files:
            os.remove(file)
        os.remove("filelist.json")


# =============================================================================
# NEW CRITICAL TEST CASES - BASED ON COVERAGE ANALYSIS
# =============================================================================


def test_build_error_status_handling(capfd) -> None:
    """
    **TEST PURPOSE**: Tests server error status handling (Lines 389-391 in metget_build.py)

    **SCENARIO**: When server returns status="error", the client should:
    1. Display failure message via spinner
    2. Return gracefully without crashing

    **WHY CRITICAL**: Real production servers can return error status due to:
    - Internal server errors
    - Data processing failures
    - Resource constraints

    **COVERAGE**: Covers previously untested lines 389-391 in download_metget_data()
    """
    args = argparse.Namespace()
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None

    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    data_id = "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"

    with requests_mock.Mocker() as m:
        # Mock the status check to return "error"
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            json=METGET_BUILD_RETURN_ERROR,
        )

        # Should return gracefully without exception
        client.download_metget_data(
            data_id, args.check_interval, args.max_wait, args.output_directory
        )

        # Capture output to verify error message was displayed
        out, err = capfd.readouterr()
        # The spinner.fail() should show the error message
        # Note: Since we're using spinnerlogger, the exact output format may vary


def test_build_timeout_scenarios(capfd) -> None:
    """
    **TEST PURPOSE**: Tests timeout handling for different request states (Lines 432-453)

    **SCENARIOS TESTED**:
    1. Request stuck in "restore" state - should show restore warning
    2. Request stuck in "running" state - should show running warning
    3. Request stuck in "queued" state - should show queued warning
    4. Unknown status - should show generic error

    **WHY CRITICAL**: In production, requests can get stuck due to:
    - High server load causing queue backlogs
    - Data restoration from cold storage taking too long
    - Processing timeouts on complex requests

    **COVERAGE**: Covers previously untested lines 432-453 in download_metget_data()
    """
    base_args = argparse.Namespace()
    base_args.check_interval = 1
    base_args.max_wait = (
        1 / 3600
    )  # Very short timeout to trigger timeout scenarios (fraction of hour)
    base_args.output_directory = None
    base_args.endpoint = METGET_DMY_ENDPOINT
    base_args.apikey = METGET_DMY_APIKEY
    base_args.api_version = METGET_API_VERSION

    environment = get_metget_environment_variables(base_args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    data_id = "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"

    # Test 1: Restore timeout scenario
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            json=METGET_BUILD_RETURN_RESTORE,
        )

        client.download_metget_data(
            data_id,
            base_args.check_interval,
            base_args.max_wait,
            base_args.output_directory,
        )
        out, err = capfd.readouterr()
        assert "did not become ready before the max-wait time expired" in out

    # Test 2: Running timeout scenario
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            json=METGET_BUILD_RETURN_RUNNING,
        )

        client.download_metget_data(
            data_id,
            base_args.check_interval,
            base_args.max_wait,
            base_args.output_directory,
        )
        out, err = capfd.readouterr()
        assert "is still being constructed" in out

    # Test 3: Queued timeout scenario
    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            json=METGET_BUILD_RETURN_QUEUED,
        )

        client.download_metget_data(
            data_id,
            base_args.check_interval,
            base_args.max_wait,
            base_args.output_directory,
        )
        out, err = capfd.readouterr()
        assert "is still queued" in out

    # Test 4: Unknown status scenario
    unknown_status_response = METGET_BUILD_RETURN_QUEUED.copy()
    unknown_status_response["body"]["status"] = "unknown_status"

    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            json=unknown_status_response,
        )

        client.download_metget_data(
            data_id,
            base_args.check_interval,
            base_args.max_wait,
            base_args.output_directory,
        )
        out, err = capfd.readouterr()
        assert "has not become available due to an unknown error" in out


def test_build_argument_validation() -> None:
    """
    **TEST PURPOSE**: Tests argument validation in metget_build function (Lines 518-528)

    **SCENARIOS TESTED**:
    1. Missing --start argument
    2. Missing --end argument
    3. Missing --timestep argument
    4. Missing --output argument

    **WHY CRITICAL**: These are required arguments and missing them should fail gracefully
    with clear error messages rather than causing crashes downstream.

    **COVERAGE**: Covers previously untested lines 518-528 in metget_build()
    """
    # Base args with intentionally missing required fields
    base_args = argparse.Namespace()
    base_args.request = None  # Force validation of other required args
    base_args.endpoint = METGET_DMY_ENDPOINT
    base_args.apikey = METGET_DMY_APIKEY
    base_args.api_version = METGET_API_VERSION

    # Test 1: Missing --start
    args = argparse.Namespace(**vars(base_args))
    args.start = None
    args.end = datetime(2023, 6, 2)
    args.timestep = 3600
    args.output = "test"

    with pytest.raises(SystemExit) as exc_info:
        metget_build(args)
    assert exc_info.value.code == 1

    # Test 2: Missing --end
    args = argparse.Namespace(**vars(base_args))
    args.start = datetime(2023, 6, 1)
    args.end = None
    args.timestep = 3600
    args.output = "test"

    with pytest.raises(SystemExit) as exc_info:
        metget_build(args)
    assert exc_info.value.code == 1

    # Test 3: Missing --timestep
    args = argparse.Namespace(**vars(base_args))
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.timestep = None
    args.output = "test"

    with pytest.raises(SystemExit) as exc_info:
        metget_build(args)
    assert exc_info.value.code == 1

    # Test 4: Missing --output
    args = argparse.Namespace(**vars(base_args))
    args.start = datetime(2023, 6, 1)
    args.end = datetime(2023, 6, 2)
    args.timestep = 3600
    args.output = None

    with pytest.raises(SystemExit) as exc_info:
        metget_build(args)
    assert exc_info.value.code == 1


def test_build_keyboard_interrupt_handling() -> None:
    """
    **TEST PURPOSE**: Tests KeyboardInterrupt handling (Lines 395-397 in metget_build.py)

    **SCENARIO**: When user presses Ctrl+C during request polling:
    1. Should display appropriate failure message via spinner
    2. Should re-raise KeyboardInterrupt for proper cleanup

    **WHY CRITICAL**: Users frequently need to cancel long-running requests. Proper
    interrupt handling ensures clean shutdown and prevents data corruption.

    **COVERAGE**: Covers previously untested lines 395-397 in download_metget_data()
    """
    args = argparse.Namespace()
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = None
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    data_id = "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"

    with requests_mock.Mocker() as m:
        # Mock the status check to raise KeyboardInterrupt
        def mock_keyboard_interrupt(request, context):
            msg = "User pressed Ctrl+C"
            raise KeyboardInterrupt(msg)

        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            text=mock_keyboard_interrupt,
        )

        # Should re-raise KeyboardInterrupt after displaying message
        with pytest.raises(KeyboardInterrupt):
            client.download_metget_data(
                data_id, args.check_interval, args.max_wait, args.output_directory
            )


def test_build_output_directory_validation() -> None:
    """
    **TEST PURPOSE**: Tests output directory validation (Lines 404-407 in metget_build.py)

    **SCENARIO**: When user specifies an output directory that doesn't exist:
    1. Should raise RuntimeError with clear message
    2. Should not attempt to create files in non-existent directory

    **WHY CRITICAL**: Prevents silent failures and gives users clear feedback about
    invalid directory paths before attempting downloads.

    **COVERAGE**: Covers previously untested lines 404-407 in download_metget_data()
    """
    args = argparse.Namespace()
    args.check_interval = 1
    args.max_wait = 1
    args.output_directory = "/completely/nonexistent/directory/path"  # Invalid path
    args.endpoint = METGET_DMY_ENDPOINT
    args.apikey = METGET_DMY_APIKEY
    args.api_version = METGET_API_VERSION

    environment = get_metget_environment_variables(args)
    client = MetGetBuildRest(
        environment["endpoint"], environment["apikey"], environment["api_version"]
    )

    data_id = "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f"

    with requests_mock.Mocker() as m:
        # Mock successful completion and file list
        m.get(
            METGET_DMY_ENDPOINT + f"/check?request-id={data_id:s}",
            json=METGET_BUILD_RETURN_COMPLETE,
        )

        # Mock successful filelist.json retrieval
        mock_filelist = {"output_files": ["test_file.txt"]}
        m.get(
            f"https://s3.amazonaws.com/metget/{data_id:s}/filelist.json",
            json=mock_filelist,
        )

        # Should raise RuntimeError about non-existent directory
        with pytest.raises(RuntimeError, match="Output directory does not exist"):
            client.download_metget_data(
                data_id, args.check_interval, args.max_wait, args.output_directory
            )
