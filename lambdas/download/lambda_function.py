#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 ADCIRC Development Group
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


def generate_default_date_range():
    from datetime import datetime
    from datetime import timedelta

    start = datetime.utcnow()
    start = datetime(start.year, start.month, start.day, 0, 0, 0) - timedelta(days=1)
    end = start + timedelta(days=2)
    return start, end


def nam_download():
    from metgetlib.ncepnamdownloader import NcepNamdownloader

    start, end = generate_default_date_range()
    nam = NcepNamdownloader(start, end)
    print(
        "[INFO]: Beginning to run NCEP-NAM from "
        + start.isoformat()
        + " to "
        + end.isoformat(),
        flush=True,
    )
    n = nam.download()
    print("[INFO]: NCEP-NAM complete. " + str(n) + " files downloaded", flush=True)
    return n


def gfs_download():
    from metgetlib.ncepgfsdownloader import NcepGfsdownloader

    start, end = generate_default_date_range()
    gfs = NcepGfsdownloader(start, end)
    print(
        "[INFO]: Beginning to run NCEP-GFS from "
        + start.isoformat()
        + " to "
        + end.isoformat(),
        flush=True,
    )
    n = gfs.download()
    print("[INFO]: NCEP-GFS complete. " + str(n) + " files downloaded", flush=True)
    return n

def gefs_download():
    from metgetlib.ncepgefsdownloader import NcepGefsdownloader

    start, end = generate_default_date_range()
    gefs = NcepGefsdownloader(start, end)
    print(
        "[INFO]: Beginning to run NCEP-GEFS from "
        + start.isoformat()
        + " to "
        + end.isoformat(),
        flush=True,
    )
    n = gefs.download()
    print("[INFO]: NCEP-GEFS complete. " + str(n) + " files downloaded", flush=True)
    return n

def hwrf_download():
    from metgetlib.hwrfdownloader import HwrfDownloader

    start, end = generate_default_date_range()
    hwrf = HwrfDownloader(start, end)
    print(
        "[INFO]: Beginning to run HWRF from "
        + start.isoformat()
        + " to "
        + end.isoformat(),
        flush=True,
    )
    n = hwrf.download()
    print("[INFO]: HWRF complete. " + str(n) + " files downloaded", flush=True)
    return n


def nhc_download():
    from metgetlib.nhcdownloader import NhcDownloader

    nhc = NhcDownloader()
    print("[INFO:] Beginning downloading NHC data")
    n = nhc.download()
    print("[INFO]: NHC complete. " + str(n) + " files downloaded", flush=True)
    return n


def coamps_download():
    from metgetlib.coampsdownloader import CoampsDownloader

    coamps = CoampsDownloader()
    print("[INFO]: Beginning downloading COAMPS data")
    n = coamps.download()
    print("[INFO]: COAMPS complete. " + str(n) + " files downloaded", flush=True)
    return n

def hrrr_download():
    from metgetlib.ncephrrrdownloader import NcepHrrrdownloader
    
    start, end = generate_default_date_range()
    hrrr = NcepHrrrdownloader(start, end)
    print("[INFO]: Beginning downloading HRRR data")
    n = hrrr.download()
    print("[INFO]: HRRR complete. " + str(n) + " files downloaded", flush=True)
    return n



def lambda_handler(event, context):
    import json
    import sys

    try:
        request_type = event["service"]
    except:
        print("[ERROR]: Malformed event")
        sys.exit(1)

    print("[INFO]: Running with configuration: " + request_type, flush=True)

    n = 0
    if request_type == "nam":
        n = nam_download()
    elif request_type == "gfs":
        n = gfs_download()
    elif request_type == "gefs":
        n = gefs_download()
    elif request_type == "hwrf":
        n = hwrf_download()
    elif request_type == "nhc":
        n = nhc_download()
    elif request_type == "coamps":
        n = coamps_download()
    elif request_type == "hrrr":
        n = hrrr_download()

    returndata = {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "download complete", "service": request_type, "nfiles": n}
        ),
    }

    print("[INFO]: Returning data: " + json.dumps(returndata, indent=2))

    return returndata


if __name__ == "__main__":
    context = ""
    event = {"service": "coamps"}
    lambda_handler(event, context)
