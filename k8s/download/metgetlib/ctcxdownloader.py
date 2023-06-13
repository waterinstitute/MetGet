import tempfile
import boto3


class CtcxDownloader:
    """
    This class is responsible for downloading the CTCX data from S3.
    """

    def __init__(self):
        """
        Initialize the downloader using the environment variables.

        Environment Variables Used:
            COAMPS_S3_BUCKET: The name of the S3 bucket to download from
            COAMPS_AWS_KEY: The AWS key to use for authentication
            COAMPS_AWS_SECRET: The AWS secret to use for authentication
        """
        import os

        self.__s3_bucket = os.environ["COAMPS_S3_BUCKET"]

        if "COAMPS_AWS_KEY" in os.environ:
            self.__aws_key_id = os.environ["COAMPS_AWS_KEY"]
        else:
            self.__aws_key_id = None

        if "COAMPS_AWS_SECRET" in os.environ:
            self.__aws_access_key = os.environ["COAMPS_AWS_SECRET"]
        else:
            self.__aws_access_key = None

        if self.__aws_key_id is None or self.__aws_access_key is None:
            self.__resource = boto3.resource("s3")
        else:
            self.__resource = boto3.resource(
                "s3",
                aws_access_key_id=self.__aws_key_id,
                aws_secret_access_key=self.__aws_access_key,
            )
        self.__bucket = self.__resource.Bucket(self.__s3_bucket)
        self.__temp_directory = tempfile.mkdtemp()

    def __del__(self):
        import shutil
        import logging
        
        log = logging.getLogger(__name__)

        log.info("Removing temporary directory")
        shutil.rmtree(self.__temp_directory)

    def download(self) -> int:
        """
        Download the CTCX data from S3.

        Returns:
            The number of files downloaded
        """
        from .metdb import Metdb
        from .s3file import S3file
        from datetime import datetime
        import os
        import shutil
        import logging

        log = logging.getLogger(__name__)

        db = Metdb()
        s3 = S3file()

        current_year = datetime.utcnow().year - 1

        storm_min = 1
        storm_max = 41

        file_count = 0

        for st in range(storm_min, storm_max, 1):
            storm_name = "{:02d}L".format(st)
            prefix = "CTCX/{:04d}/{:s}/".format(current_year, storm_name)
            objects = self.__bucket.objects.filter(Prefix=prefix)
            for obj in objects:
                path = obj.key

                info = self.__retrieve_files_from_s3(path, storm_name)
                archive_filename = info["filename"]

                # ...Get the base name of the file (without the extension)
                base_name = archive_filename[: -len(".tar.gz")]
                
                ensemble_member_list = []

                # ...Convert the hdf5 files to netCDF format
                log.info("Begin converting hdf5 files to netCDF format")
                
                directory = os.path.join(self.__temp_directory, base_name)
                log.info("Working on directory {:s}".format(directory))
                for filename in os.listdir(directory):
                    if filename.endswith(".hdf5"):
                        ensemble_member_list.append(
                            self.__process_hdf5_file(base_name, filename)
                        )
                        file_count += ensemble_member_list[-1]["n_snaps"]

                shutil.rmtree(directory)

        return file_count

    def __retrieve_files_from_s3(self, path: str, storm_name: str) -> dict:
        """
        Retrieve the files from S3 and return a dict with the metadata.

        Args:
            path: The path to the file in S3
            storm_name: The name of the storm

        Returns:
            A dict with the metadata
        """
        import os
        from datetime import datetime
        import tarfile
        import logging

        log = logging.getLogger(__name__)

        # ...Get the metadata from the filename
        filename = os.path.basename(path)
        cycle_date = datetime.strptime(
            filename, "CTCXEPS_{:s}.%Y%m%d%H.tar.gz".format(storm_name)
        )

        # ...Retrieve file from S3
        log.info("Begin downloading file {:s} from s3".format(path))
        local_file = os.path.join(self.__temp_directory, filename)
        self.__bucket.download_file(path, local_file)

        # ...Unpack the tarball
        log.info("Begin unpacking file {:s}".format(local_file))
        tar = tarfile.open(local_file)
        tar.extractall(path=self.__temp_directory)
        tar.close()

        return {
            "filename": filename,
            "cycle_date": cycle_date,
        }

    def __process_hdf5_file(self, base_name: str, filename: str) -> dict:
        """
        Process the hdf5 file and convert it to netCDF format and return a dict with the metadata.

        Args:
            base_name: The base name of the file (without the extension)
            filename: The name of the file

        Returns:
            A dict with the metadata
        """
        from .ctcxformatter import CtcxFormatter
        import logging
        import os

        log = logging.getLogger(__name__)

        ensemble_member = int(filename.split("_")[0][-3:])
        ensemble_member_str = "{:03d}".format(ensemble_member)
        member_directory = os.path.join(self.__temp_directory, base_name, ensemble_member_str)
        os.mkdir(member_directory)
        log.info(
            "Processing ensemble member {:d} in folder {:s}".format(
                ensemble_member, member_directory
            )
        )
        formatter = CtcxFormatter(
            os.path.join(self.__temp_directory, base_name, filename),
            member_directory,
        )
        n_snaps = formatter.n_time_steps()
        formatter.write()

        return {
            "member": ensemble_member_str,
            "directory": member_directory,
            "n_snaps": n_snaps,
        }
