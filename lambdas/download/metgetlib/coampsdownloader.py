#!/usr/bin/env python3

from datetime import datetime

DEBUG_LEVEL = 1


def logger(message, level=0):
    if level > DEBUG_LEVEL:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("[{}]: {}".format(now, message), flush=True)


class CoampsDownloader:
    def __init__(self):
        from ftplib import FTP

        self.__ftp_site = "ftp-ex.nrlmry.navy.mil"
        self.__folder = "send"
        self.__ftp_client = None

    def __connect(self):
        from ftplib import FTP
        import sys

        try:
            logger("Connecting to " + self.__ftp_site)
            self.__ftp_client = FTP(self.__ftp_site)
            self.__ftp_client.login()
            self.__ftp_client.cwd(self.__folder)
        except Exception as e:
            logger("Could not start FTP session: " + str(e), 5)
            sys.exit(1)
        logger("Connected to " + self.__ftp_site, 1)

    def __disconnect(self):
        self.__ftp_client.quit()

    def download(self):
        from .metdb import Metdb
        from .s3file import S3file
        from datetime import timedelta
        import os

        db = Metdb()
        s3 = S3file(os.environ["BUCKET_NAME"])

        forecast_delta_time = 3600 * 6

        storm_min = 1
        storm_max = 41

        temp_date_min = datetime.utcnow() - timedelta(days=5)
        temp_date_max = datetime.utcnow() + timedelta(days=1)

        date_min = datetime(
            temp_date_min.year, temp_date_min.month, temp_date_min.day, 0, 0, 0
        )
        date_max = datetime(
            temp_date_max.year, temp_date_max.month, temp_date_max.day, 0, 0, 0
        )

        self.__connect()

        for st in range(storm_min, storm_max, 1):
            storm_name = "{:02d}L".format(st)
            start_timestamp = int(date_min.timestamp())
            end_timestamp = int(date_max.timestamp())
            for dt in range(
                int(date_min.timestamp()),
                int(date_max.timestamp()),
                forecast_delta_time,
            ):
                current_date = datetime.fromtimestamp(dt)

                # ...Check if it exists in the database already
                data_pair = {
                    "cycledate": current_date,
                    "forecastdate": current_date,
                    "name": storm_name,
                }
                exists = db.has("coamps", data_pair)
                if not exists:
                    status, filename = self.__get(storm_name, current_date)
                    if status:
                        temporary_folder = CoampsDownloader.unpack(storm_name, filename)
                        file_list = CoampsDownloader.get_file_list(temporary_folder)

                        for key in file_list.keys():
                            dd = file_list[key]
                            files = ""
                            data_pair = {
                                "cycledate": file_list[key][0]["cycle"],
                                "forecastdate": key,
                                "name": storm_name,
                            }
                            for f in dd:
                                local_file = f["filename"]
                                cycle = f["cycle"]
                                remote_path = "coamps_tc/"+storm_name+"/"+datetime.strftime(cycle, "%Y%m%d/%H")+"/"+os.path.basename(f["filename"])
                                s3.upload_file(local_file, remote_path)
                                if files == "":
                                    files += remote_path
                                else:
                                    files += "," + remote_path
                            db.add(data_pair, "coamps", files) 
                        CoampsDownloader.wipe(temporary_folder)
                        os.remove(filename)

        self.__disconnect()

    def __get(self, storm, date): 
        import os
        import ftplib
        import tempfile

        filename = "{}_{}_netcdf.tar".format(storm, date.strftime("%Y%m%d%H"))
        if not os.path.exists(filename):
            logger("Attempting to fetch file: {}".format(filename), 1)

            # ...Check if file exists. Use size method on a known
            # filename since the list methods are disabled on the
            # coamps ftp server
            try:
                file_size = self.__ftp_client.size(filename)
                logger("File {} found on server".format(filename), 3)
            except ftplib.error_perm as e:
                logger("File {} not found on server".format(filename), 1)
                return False, ""

            # ...If the file exists, then download
            floc = tempfile.gettempdir() + "/" + filename
            try:
                logger("Starting to download filename: {}".format(filename))
                self.__ftp_client.retrbinary(
                    "RETR {}".format(filename), open(floc, "wb").write
                )
            except Exception as e:
                os.remove(floc)
                logger(
                    "Could not retrieve specified file: {}, Error:  {}".format(
                        filename, str(e), 5
                    )
                )
                self.__disconnect()
                return False, ""
            logger("Got file {}".format(floc))
            return True, floc
        else:
            return False, ""

    @staticmethod
    def unpack(storm, filename) -> str:
        import tarfile
        import tempfile

        if not tarfile.is_tarfile(filename):
            logger("[ERROR]: Invalid tarfile: {}".format(filename), 5)

        tempdir = tempfile.mkdtemp(prefix="coamps_")
        with tarfile.open(filename, "r") as tar:
            tar.extractall(tempdir)
        return tempdir

    @staticmethod
    def wipe(folder) -> bool:
        import shutil

        shutil.rmtree(folder)

    @staticmethod
    def __sql_time_format(time) -> str:
        return datetime.strftime(time, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def __date_from_filename(filename):
        from datetime import timedelta

        forecast_nhour = int(filename[-6:-3])
        date_str = filename[-20:-10]
        cycle_hour = datetime.strptime(date_str, "%Y%m%d%H")
        forecast_hour = cycle_hour + timedelta(hours=forecast_nhour)
        return cycle_hour, forecast_hour

    def get_file_list(folder) -> dict:
        import glob

        path = "{}/netcdf/*.nc".format(folder)

        filenames = sorted(glob.glob(path, recursive=True))
        data = {}
        for f in filenames:
            cycle_date, forecast_hour = CoampsDownloader.__date_from_filename(f)
            domain = int(f[-23:-22])
            if forecast_hour not in data.keys():
                data[forecast_hour] = []

            data[forecast_hour].append(
                {"cycle": cycle_date, "domain": domain, "filename": f}
            )
        return data
