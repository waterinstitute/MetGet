#!/usr/bin/env python3
###################################################################################################
# MIT License
#
# Copyright (c) 2023 The Water Institute
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
#
# Author: Zach Cobell
# Contact: zcobell@thewaterinstitute.org
# Organization: The Water Institute
#
###################################################################################################

def generate_default_date_range():
    from datetime import datetime
    from datetime import timedelta

    start = datetime.utcnow()
    start = datetime(start.year, start.month, start.day, 0, 0, 0) - timedelta(days=1)
    end = start + timedelta(days=2)
    return start, end


def nam_download():
    from metgetlib.ncepnamdownloader import NcepNamdownloader
    import logging

    logger = logging.getLogger(__name__)

    start, end = generate_default_date_range()
    nam = NcepNamdownloader(start, end)
    logger.info(
        "Beginning to run NCEP-NAM from {:s} to {:s}".format(
            start.isoformat(), end.isoformat()
        )
    )
    n = nam.download()
    logger.info("NCEP-NAM complete. " + str(n) + " files downloaded")
    return n


def gfs_download():
    from metgetlib.ncepgfsdownloader import NcepGfsdownloader
    import logging

    logger = logging.getLogger(__name__)

    start, end = generate_default_date_range()
    gfs = NcepGfsdownloader(start, end)
    logger.info(
        "Beginning to run NCEP-GFS from {:s} to {:s}".format(
            start.isoformat(), end.isoformat()
        )
    )
    n = gfs.download()
    logger.info("NCEP-GFS complete. {:d} files downloaded".format(n))
    return n


def gefs_download():
    from metgetlib.ncepgefsdownloader import NcepGefsdownloader
    import logging

    logger = logging.getLogger(__name__)

    start, end = generate_default_date_range()
    gefs = NcepGefsdownloader(start, end)
    logger.info(
        "Beginning to run NCEP-GEFS from {:s} to {:s}".format(
            start.isoformat(), end.isoformat()
        )
    )
    n = gefs.download()
    logger.info("NCEP-GEFS complete. {:d} files downloaded".format(n))
    return n


def hwrf_download():
    from metgetlib.hwrfdownloader import HwrfDownloader
    import logging

    logger = logging.getLogger(__name__)

    start, end = generate_default_date_range()
    hwrf = HwrfDownloader(start, end)
    logger.info(
        "Beginning to run HWRF from {:s} to {:s}".format(
            start.isoformat(), end.isoformat()
        )
    )
    n = hwrf.download()
    logger.info("HWRF complete. {:d} files downloaded".format(n))
    return n


def nhc_download():
    from metgetlib.nhcdownloader import NhcDownloader
    import logging

    logger = logging.getLogger(__name__)

    nhc = NhcDownloader()
    logger.info("Beginning downloading NHC data")
    n = nhc.download()
    logger.info("NHC complete. {:d} files downloaded".format(n))
    return n


def coamps_download():
    from metgetlib.coampsdownloader import CoampsDownloader
    import logging

    logger = logging.getLogger(__name__)

    coamps = CoampsDownloader()
    logger.info("Beginning downloading COAMPS data")
    n = coamps.download()
    logger.info("COAMPS complete. {:d} files downloaded".format(n))
    return n


def ctcx_download():
    from metgetlib.ctcxdownloader import CtcxDownloader
    import logging

    logger = logging.getLogger(__name__)

    ctcx = CtcxDownloader()
    n = ctcx.download()
    logger.info("CTCX complete. {:d} files downloaded".format(n))
    return n


def hrrr_download():
    from metgetlib.ncephrrrdownloader import NcepHrrrdownloader
    import logging

    logger = logging.getLogger(__name__)

    start, end = generate_default_date_range()
    hrrr = NcepHrrrdownloader(start, end)
    logger.info("Beginning downloading HRRR data")
    n = hrrr.download()

    logger.info("HRRR complete. {:d} files downloaded".format(n))
    return n


def hrrr_alaska_download():
    from metgetlib.ncephrrralaskadownloader import NcepHrrrAlaskadownloader
    import logging

    logger = logging.getLogger(__name__)

    start, end = generate_default_date_range()
    hrrr = NcepHrrrAlaskadownloader(start, end)
    logger.info("Beginning downloading HRRR-Alaska data")
    n = hrrr.download()
    logger.info("HRRR complete. {:d} files downloaded".format(n))
    return n


def wpc_download():
    from metgetlib.wpcdownloader import WpcDownloader
    import logging

    logger = logging.getLogger(__name__)

    start, end = generate_default_date_range()
    wpc = WpcDownloader(start, end)
    logger.info("Beginning downloading WPC data")
    n = wpc.download()
    logger.info("WPC complete. {:d} files downloaded".format(n))
    return n


def main():
    import argparse
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s :: %(levelname)s :: %(module)s :: %(message)s",
    )
    logger = logging.getLogger(__name__)

    p = argparse.ArgumentParser(description="MetGet Download Function")
    p.add_argument(
        "--service",
        type=str,
        required=True,
        help="Service to download from (nam, gfs, gefs, hwrf, nhc, coamps, hrrr, hrrr-alaska, wpc)",
    )
    args = p.parse_args()

    logger.info("Running with configuration: {:s}".format(args.service))

    if args.service == "nam":
        n = nam_download()
    elif args.service == "gfs":
        n = gfs_download()
    elif args.service == "gefs":
        n = gefs_download()
    elif args.service == "hwrf":
        n = hwrf_download()
    elif args.service == "nhc":
        n = nhc_download()
    elif args.service == "coamps":
        n = coamps_download()
    elif args.service == "ctcx":
        n = ctcx_download()
    elif args.service == "hrrr":
        n = hrrr_download()
    elif args.service == "hrrr-alaska":
        n = hrrr_alaska_download()
    elif args.service == "wpc":
        n = wpc_download()
    else:
        raise RuntimeError("Invalid data source selected")


if __name__ == "__main__":
    main()
