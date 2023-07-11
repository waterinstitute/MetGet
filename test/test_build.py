import argparse
from datetime import datetime

import requests_mock
from .build_json import *
from metget_client.metget_build import MetGetBuildRest
from metget_client.metget_environment import get_metget_environment_variables

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
    args.max_wait = 3600

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
    Tests the build request for a multi domain hwrf+gfs data
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
    args.max_wait = 3600

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
    Tests the build request for a multi domain hwrf+gfs data
    Args:
        capfd: pytest fixture to capture stdout and stderr

    Returns:
        None
    """
    import json
    import os
    from metget_client.metget_build import metget_build

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
    args.max_wait = 3600
    args.request = None
    args.compression = False
    args.save_json_request = True

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
            METGET_DMY_ENDPOINT + "/check?request-id={:s}".format(data_id),
            response_list,
        )
        data_id, status_code = client.make_metget_request(request_dict)
        with open(path, "rb") as filelist_file:
            filelist_data = json.load(filelist_file)
            m.get(
                "https://s3.amazonaws.com/metget/{:s}/filelist.json".format(data_id),
                json=filelist_data,
            )

            for file in output_files:
                m.get(
                    "https://s3.amazonaws.com/metget/{:s}/{:s}".format(data_id, file),
                    text="This is only a test",
                )

            metget_build(args)

            for file in output_files:
                assert os.path.exists(file)
                os.remove(file)
            os.remove("filelist.json")
            os.remove("request.json")


def metget_request_mocker(
    data_id: str,
    client: MetGetBuildRest,
    output_files: list,
    filelist_file: str,
    args: argparse.Namespace,
    capfd,
) -> None:
    import os
    import json

    response_list = [
        {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
        {"json": METGET_BUILD_RETURN_QUEUED, "status_code": 200},
        {"json": METGET_BUILD_RETURN_RUNNING, "status_code": 200},
        {"json": METGET_BUILD_RETURN_COMPLETE, "status_code": 200},
    ]

    with requests_mock.Mocker() as m:
        m.get(
            METGET_DMY_ENDPOINT + "/check?request-id={:s}".format(data_id),
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
                "https://s3.amazonaws.com/metget/{:s}/filelist.json".format(data_id),
                json=filelist_data,
            )

            for file in output_files:
                m.get(
                    "https://s3.amazonaws.com/metget/{:s}/{:s}".format(data_id, file),
                    text="This is only a test",
                )

            client.download_metget_data(data_id, args.check_interval, args.max_wait)
            out, err = capfd.readouterr()

        # ...Clean up
        for file in output_files:
            os.remove(file)
        os.remove("filelist.json")
