from typing import Union, List, Tuple
import logging


class S3GribIO:
    """
    Class which handles the download of specific chunks
    of grib data from s3 resources
    """

    def __init__(self, s3_bucket: str, variable_list: dict):
        """
        Constructor

        Args:
            s3_bucket (str): The s3 bucket to download from
            variable_list (dict): The list of variables to download
        """
        import boto3

        self.__s3_bucket = s3_bucket
        self.__s3_client = boto3.client("s3")
        self.__s3_resource = boto3.resource("s3")
        self.__s3_bucket_object = self.__s3_resource.Bucket(self.__s3_bucket)

        self.__variable_list = []
        for variable in variable_list.keys():
            self.__variable_list.append(
                {
                    "long_name": variable_list[variable],
                    "name": variable,
                }
            )

    def s3_bucket(self) -> str:
        """
        Returns the s3 bucket

        Returns:
            str: The s3 bucket
        """
        return self.__s3_bucket

    def variable_list(self) -> List[dict]:
        """
        Returns the variable list

        Returns:
            list: The variable list
        """
        return self.__variable_list

    @staticmethod
    def __parse_path(path: str) -> Tuple[str, str]:
        """
        Parses the s3://bucket/path/to/file formatted
        path into the name of the bucket and the file path

        Args:
            path (str): The path to parse

        Returns:
            Tuple containing the bucket name and the file path
        """
        from urllib.parse import urlparse

        result = urlparse(path)
        return result.netloc, result.path.lstrip("/")

    def __try_get_object(self, key: str, byte_range: str = None) -> dict:
        """
        Try to get an object from a s3 bucket. If the object does not exist, wait 5 seconds and try again.

        Args:
            key (str): The key of the object
            byte_range (str): The byte range to get

        Returns:
            The object from the bucket
        """
        from botocore.exceptions import ClientError
        from time import sleep

        max_tries = 5
        sleep_interval = 5
        tries = 0

        while True:
            try:
                if byte_range:
                    return self.__s3_client.get_object(
                        Bucket=self.__s3_bucket, Key=key, Range=byte_range
                    )
                else:
                    return self.__s3_client.get_object(Bucket=self.__s3_bucket, Key=key)
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    tries += 1
                    sleep(sleep_interval)
                    if tries > max_tries:
                        raise RuntimeError(
                            "Could not find key {} in bucket {}".format(
                                key, self.__s3_bucket
                            )
                        )
                else:
                    raise e

    @staticmethod
    def __get_inventory_byte_list(
        inventory_data: list, variable: dict
    ) -> Union[dict, None]:
        """
        Gets the byte list for the variable from the inventory data

        Args:
            inventory_data (list): The inventory data
            variable (dict): The variable dictionary

        Returns:
            dict: The byte list for the variable
        """
        log = logging.getLogger(__name__)
        for i in range(len(inventory_data)):
            if variable["long_name"] in inventory_data[i]:
                start_bits = inventory_data[i].split(":")[1]
                if i + 1 == len(inventory_data):
                    end_bits = ""
                else:
                    end_bits = inventory_data[i + 1].split(":")[1]
                return {"name": variable["name"], "start": start_bits, "end": end_bits}
        return None

    def __get_grib_inventory(self, s3_file: str) -> list:
        """
        Gets the inventory for the grib file

        Args:
            s3_file (str): The s3 file to get the inventory for

        Returns:
            list: The inventory for the grib file
        """
        inv_obj = self.__try_get_object(s3_file + ".idx")
        inv_data_tmp = str(inv_obj["Body"].read().decode("utf-8")).split("\n")
        inv_data = []
        for line in inv_data_tmp:
            if not line == "":
                inv_data.append(line)
        byte_list = []
        for v in self.__variable_list:
            byte_list.append(S3GribIO.__get_inventory_byte_list(inv_data, v))

        return byte_list

    def download(self, s3_file: str, local_file: str) -> bool:
        """
        Downloads the grib file from s3 to the local file path
        for the variables specified in the variable list

        Args:
            s3_file (str): The s3 file to download
            local_file (str): The local file path to download to

        Returns:
            bool: True if the download was successful, False otherwise
        """
        log = logging.getLogger(__name__)

        bucket, path = self.__parse_path(s3_file)
        if bucket != self.__s3_bucket:
            log.error(
                "Bucket {} does not match expected bucket {}".format(
                    bucket, self.__s3_bucket
                )
            )
            return False

        inventory = self.__get_grib_inventory(path)

        if len(inventory) == 0:
            log.error("No inventory found for file {}".format(path))
            return False
        elif len(inventory) != len(self.__variable_list):
            log.error("Inventory length does not match variable list length")
            return False

        log.info("Downloading {} to {}".format(s3_file, local_file))

        for var in inventory:
            byte_range = "bytes={}-{}".format(var["start"], var["end"])
            obj = self.__try_get_object(path, byte_range)
            with open(local_file, "ab") as f:
                f.write(obj["Body"].read())

        return True
