from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
import enum

# This is the base class for all the tables
TableBase = declarative_base()


class AuthTable(TableBase):
    """
    This class is used to create the table that holds the API keys
    which are used to authenticate users
    """

    import os

    __tablename__ = os.environ["METGET_API_KEY_TABLE"]
    id = Column(Integer, primary_key=True)
    key = Column(String)
    username = Column(String)
    description = Column(String)
    credit_limit = Column(BigInteger)
    enabled = Column(Boolean)
    expiration = Column(DateTime)
    permissions = Column(MutableDict.as_mutable(JSONB))


class RequestEnum(enum.Enum):
    """
    This class is used to create the enum for the request status which
    is used to track the status of a request through the system
    """

    queued = 0
    running = 1
    error = 2
    completed = 3


class RequestTable(TableBase):
    """
    This class is used to create the table that holds the requests which are currently
    being processed or have been fulfilled by the system
    """

    import os

    __tablename__ = os.environ["METGET_REQUEST_TABLE"]

    index = Column("id", Integer, primary_key=True)
    request_id = Column(String)
    try_count = Column("try", Integer)
    status = Column(Enum(RequestEnum))
    start_date = Column(DateTime)
    last_date = Column(DateTime)
    api_key = Column(String)
    source_ip = Column(String)
    credit_usage = Column(BigInteger)
    input_data = Column(MutableDict.as_mutable(JSONB))
    message = Column(MutableDict.as_mutable(JSONB))

    @staticmethod
    def add_request(
        request_id: str,
        request_status: RequestEnum,
        api_key: str,
        source_ip: str,
        input_data: dict,
        message: str,
        credit: int,
    ) -> None:
        """
        This method is used to add a new request to the database

        Args:
            request_id (str): The request ID
            request_status (RequestEnum): The status of the request
            api_key (str): The API key used to authenticate the request
            source_ip (str): The IP address of the source of the request
            input_data (dict): The input data for the request
            message (str): The message for the request
            credit (int): The number of credits used for the request

        Returns:
            None
        """
        from datetime import datetime
        from metbuild.database import Database

        record = RequestTable(
            request_id=request_id,
            try_count=0,
            status=request_status,
            start_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            last_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            api_key=api_key,
            source_ip=source_ip,
            input_data=input_data,
            credit_usage=credit,
            message={"message": message},
        )

        with Database() as db, db.session() as session:
            qry_object = session.query(RequestTable).where(
                RequestTable.request_id == record.request_id
            )
            if qry_object.first() is None:
                session.add(record)
                session.commit()

    @staticmethod
    def update_request(
        request_id: str,
        request_status: RequestEnum,
        api_key: str,
        source_ip: str,
        input_data: dict,
        message: str,
        credit: int,
        increment_try: bool = False,
    ) -> None:
        """
        This method is used to update a request in the database

        Args:
            request_id (str): The request ID
            request_status (RequestEnum): The status of the request
            api_key (str): The API key used to authenticate the request
            source_ip (str): The IP address of the source of the request
            input_data (dict): The input data for the request
            message (str): The message for the request
            credit (int): The number of credits used for the request
            increment_try (bool): Whether to increment the try count

        Returns:
            None
        """
        from datetime import datetime
        from metbuild.database import Database

        with Database() as db, db.session() as session:
            record = (
                session.query(RequestTable)
                .where(RequestTable.request_id == request_id)
                .first()
            )

            if record is None:
                RequestTable.add_request(
                    request_id,
                    request_status,
                    api_key,
                    source_ip,
                    input_data,
                    message,
                    credit,
                )
            else:
                if increment_try:
                    record.try_count += 1
                record.status = request_status
                record.last_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                record.message = {"message": message}
                session.commit()


class GfsTable(TableBase):
    """
    This class is used to create the table that holds the GFS data which has been
    downloaded from the NCEP server
    """

    __tablename__ = "gfs_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class NamTable(TableBase):
    """
    This class is used to create the table that holds the NAM data which has been
    downloaded from the NCEP server
    """

    __tablename__ = "nam_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class HwrfTable(TableBase):
    """
    This class is used to create the table that holds the HWRF data which has been
    downloaded from the NCEP server
    """

    __tablename__ = "hwrf"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    stormname = Column(String)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class GefsTable(TableBase):
    """
    This class is used to create the table that holds the GEFS data which has been
    downloaded from the NCEP server
    """

    __tablename__ = "gefs_fcst"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    ensemble_member = Column(String)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class CoampsTable(TableBase):
    """
    This class is used to create the table that holds the COAMPS data which has been
    downloaded from the NRL server
    """

    __tablename__ = "coamps_tc"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    stormname = Column(String)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    accessed = Column(DateTime)


class CtcxTable(TableBase):
    """
    This class is used to create the table that holds the CTCX data which has been
    downloaded from the S3 postings from NRL
    """

    __tablename__ = "ctcx"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    stormname = Column(String)
    ensemble_member = Column(Integer)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    accessed = Column(DateTime)


class HrrrTable(TableBase):
    """
    This class is used to create the table that holds the HRRR data which has beenq
    downloaded from the NCEP server
    """

    __tablename__ = "hrrr_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class HrrrAlaskaTable(TableBase):
    """
    This class is used to create the table that holds the HRRR Alaska data which has been
    downloaded from the NCEP server
    """

    __tablename__ = "hrrr_alaska_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class WpcTable(TableBase):
    """
    This class is used to create the table that holds the WPC data which has been
    downloaded from the NCEP server
    """

    __tablename__ = "wpc_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class NhcBtkTable(TableBase):
    """
    This class is used to create the table that holds the NHC Best Track data which has been
    downloaded from the NHC ftp server
    """

    from sqlalchemy import Column, Integer, String, DateTime

    __tablename__ = "nhc_btk"

    index = Column("id", Integer, primary_key=True)
    storm_year = Column(Integer)
    basin = Column(String)
    storm = Column(Integer)
    advisory_start = Column(DateTime)
    advisory_end = Column(DateTime)
    advisory_duration_hr = Column(Integer)
    filepath = Column(String)
    md5 = Column(String)
    accessed = Column(DateTime)
    geometry_data = Column(MutableDict.as_mutable(JSONB))


class NhcFcstTable(TableBase):
    """
    This class is used to create the table that holds the NHC Forecast data which has been
    processed from the NHC RSS feed
    """

    from sqlalchemy import Column, Integer, String, DateTime

    __tablename__ = "nhc_fcst"

    index = Column("id", Integer, primary_key=True)
    storm_year = Column(Integer)
    basin = Column(String)
    storm = Column(Integer)
    advisory = Column(String)
    advisory_start = Column(DateTime)
    advisory_end = Column(DateTime)
    advisory_duration_hr = Column(Integer)
    filepath = Column(String)
    md5 = Column(String)
    accessed = Column(DateTime)
    geometry_data = Column(MutableDict.as_mutable(JSONB))
