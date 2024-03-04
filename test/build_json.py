from datetime import datetime

METGET_BUILD_GFS_JSON = {
    "version": "0.0.1",
    "creator": "pytest",
    "background_pressure": 1013.0,
    "backfill": False,
    "nowcast": False,
    "multiple_forecasts": True,
    "start_date": "2023-06-01 00:00:00",
    "end_date": "2023-06-02 00:00:00",
    "format": None,
    "data_type": "wind_pressure",
    "time_step": 3600,
    "domains": [
        {
            "name": "gfs",
            "service": "gfs-ncep",
            "x_init": -100.0,
            "y_init": 10.0,
            "x_end": -80.0,
            "y_end": 30.0,
            "di": 0.25,
            "dj": 0.25,
            "level": 0,
        }
    ],
    "compression": False,
    "epsg": 4326,
    "filename": "test_build_gfs",
    "dry_run": False,
    "strict": False,
}

METGET_BUILD_GEFS_JSON = {
    "version": "0.0.1",
    "creator": "pytest",
    "background_pressure": 1013.0,
    "backfill": False,
    "nowcast": False,
    "multiple_forecasts": True,
    "start_date": "2023-06-01 00:00:00",
    "end_date": "2023-06-02 00:00:00",
    "format": None,
    "data_type": "wind_pressure",
    "time_step": 3600,
    "domains": [
        {
            "name": "gefs",
            "service": "gefs-ncep",
            "x_init": -100.0,
            "y_init": 10.0,
            "x_end": -80.0,
            "y_end": 30.0,
            "di": 0.25,
            "dj": 0.25,
            "ensemble_member": "c00",
            "level": 0,
        }
    ],
    "compression": False,
    "epsg": 4326,
    "filename": "test_build_gefs",
    "dry_run": False,
    "strict": False,
}

METGET_BUILD_COAMPS_JSON = {
    "version": "0.0.1",
    "creator": "pytest",
    "background_pressure": 1013.0,
    "backfill": False,
    "nowcast": False,
    "multiple_forecasts": True,
    "start_date": "2023-06-01 00:00:00",
    "end_date": "2023-06-02 00:00:00",
    "format": None,
    "data_type": "wind_pressure",
    "time_step": 3600,
    "domains": [
        {
            "name": "coamps-tc-09L",
            "service": "coamps-tc",
            "x_init": -100.0,
            "y_init": 10.0,
            "x_end": -80.0,
            "y_end": 30.0,
            "di": 0.25,
            "dj": 0.25,
            "storm": "09L",
            "level": 0,
            "tau": 0,
        }
    ],
    "compression": False,
    "epsg": 4326,
    "filename": "test_build_coamps",
    "dry_run": False,
    "strict": False,
}

METGET_BUILD_CTCX_JSON = {
    "version": "0.0.1",
    "creator": "pytest",
    "background_pressure": 1013.0,
    "backfill": False,
    "nowcast": False,
    "multiple_forecasts": True,
    "start_date": "2023-06-01 00:00:00",
    "end_date": "2023-06-02 00:00:00",
    "format": None,
    "data_type": "wind_pressure",
    "time_step": 3600,
    "domains": [
        {
            "name": "coamps-ctcx-09L-01",
            "service": "coamps-ctcx",
            "x_init": -100.0,
            "y_init": 10.0,
            "x_end": -80.0,
            "y_end": 30.0,
            "di": 0.25,
            "dj": 0.25,
            "ensemble_member": "01",
            "storm": "09L",
            "tau": 4,
            "level": 0,
        }
    ],
    "compression": False,
    "epsg": 4326,
    "filename": "test_build_ctcx",
    "dry_run": False,
    "strict": False,
}

METGET_BUILD_HWRF_JSON = {
    "version": "0.0.1",
    "creator": "pytest",
    "background_pressure": 1013.0,
    "backfill": False,
    "nowcast": False,
    "multiple_forecasts": True,
    "start_date": "2023-06-19 00:00:00",
    "end_date": "2023-06-24 00:00:00",
    "format": None,
    "data_type": "wind_pressure",
    "time_step": 3600,
    "domains": [
        {
            "name": "gfs",
            "service": "gfs-ncep",
            "x_init": -100.0,
            "y_init": 10.0,
            "x_end": -70.0,
            "y_end": 30.0,
            "di": 0.25,
            "dj": 0.25,
            "level": 0,
        },
        {
            "name": "hwrf-bret03l",
            "service": "hwrf",
            "storm": "bret03l",
            "tau": 0,
            "x_init": -90.0,
            "y_init": 15.0,
            "x_end": -80.0,
            "y_end": 25.0,
            "di": 0.1,
            "dj": 0.1,
            "level": 1,
        },
    ],
    "compression": False,
    "epsg": 4326,
    "filename": "test_build_hwrf",
    "strict": False,
    "dry_run": False,
}

METGET_BUILD_NHC_JSON = {
    "version": "0.0.1",
    "creator": "pytest",
    "background_pressure": 1013.0,
    "backfill": False,
    "nowcast": False,
    "multiple_forecasts": True,
    "start_date": "2023-06-19 00:00:00",
    "end_date": "2023-06-24 00:00:00",
    "format": "raw",
    "data_type": "wind_pressure",
    "time_step": 3600,
    "domains": [
        {
            "name": "nhc",
            "service": "nhc",
            "basin": "al",
            "storm": "09",
            "storm_year": 2023,
            "advisory": "015",
            "x_init": -90.0,
            "y_init": 15.0,
            "x_end": -80.0,
            "y_end": 25.0,
            "di": 0.1,
            "dj": 0.1,
            "level": 0,
        }
    ],
    "compression": False,
    "epsg": 4326,
    "filename": "test_build_nhc",
    "strict": False,
    "dry_run": False,
}

METGET_BUILD_NHC_JSON_THIS_YEAR = {
    "version": "0.0.1",
    "creator": "pytest",
    "background_pressure": 1013.0,
    "backfill": False,
    "nowcast": False,
    "multiple_forecasts": True,
    "start_date": "2023-06-19 00:00:00",
    "end_date": "2023-06-24 00:00:00",
    "format": "raw",
    "data_type": "wind_pressure",
    "time_step": 3600,
    "domains": [
        {
            "name": "nhc",
            "service": "nhc",
            "basin": "al",
            "storm": "09",
            "storm_year": datetime.utcnow().year,
            "advisory": "015",
            "x_init": -90.0,
            "y_init": 15.0,
            "x_end": -80.0,
            "y_end": 25.0,
            "di": 0.1,
            "dj": 0.1,
            "level": 0,
        }
    ],
    "compression": False,
    "epsg": 4326,
    "filename": "test_build_nhc",
    "strict": False,
    "dry_run": False,
}


METGET_BUILD_POST_RETURN = {
    "statusCode": 200,
    "body": {
        "request_id": "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f",
        "status": "queued",
        "message": "Request queued",
    },
}


METGET_BUILD_RETURN_QUEUED = {
    "statusCode": 200,
    "body": {
        "request_id": "5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f",
        "status": "queued",
        "message": "Request queued",
        "destination": "https://s3.amazonaws.com/metget/5f9b5b3c-5b7a-4c5e-8b0a-1b5b3c5d7e8f",
    },
}

METGET_BUILD_RETURN_RESTORE = METGET_BUILD_RETURN_QUEUED
METGET_BUILD_RETURN_RESTORE["body"]["status"] = "restore"
METGET_BUILD_RETURN_RESTORE["body"]["message"] = "Data in restore state"

METGET_BUILD_RETURN_RUNNING = METGET_BUILD_RETURN_QUEUED
METGET_BUILD_RETURN_RUNNING["body"]["status"] = "running"
METGET_BUILD_RETURN_RUNNING["body"]["message"] = "Request running"

METGET_BUILD_RETURN_COMPLETE = METGET_BUILD_RETURN_QUEUED
METGET_BUILD_RETURN_COMPLETE["body"]["status"] = "completed"
METGET_BUILD_RETURN_COMPLETE["body"]["message"] = "Request complete"
