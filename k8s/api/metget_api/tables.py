from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
import enum

table_base = declarative_base()


class AuthTable(table_base):
    import os

    __tablename__ = os.environ["METGET_API_KEY_TABLE"]
    id = Column(Integer, primary_key=True)
    key = Column(String)
    username = Column(String)
    description = Column(String)
    enabled = Column(Boolean)


class RequestEnum(enum.Enum):
    queued = 0
    running = 1
    error = 2
    completed = 3


class RequestTable(table_base):
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.mutable import MutableDict
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
    input_data = Column(MutableDict.as_mutable(JSONB))


class GfsTable(table_base):
    __tablename__ = "gfs_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class NamTable(table_base):
    __tablename__ = "nam_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class HwrfTable(table_base):
    __tablename__ = "hwrf"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    stormname = Column(String)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class GefsTable(table_base):
    from sqlalchemy import Column, String

    __tablename__ = "gefs_fcst"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    ensemble_member = Column(String)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class CoampsTable(table_base):
    from sqlalchemy import Column, String

    __tablename__ = "coamps_tc"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    stormname = Column(String)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class HrrrTable(table_base):
    __tablename__ = "hrrr_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class HrrrAlaskaTable(table_base):
    __tablename__ = "hrrr_alaska_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class WpcTable(table_base):
    __tablename__ = "wpc_ncep"
    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class NhcBtkTable(table_base):
    from sqlalchemy import Column, Integer, String, DateTime
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.mutable import MutableDict

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


class NhcFcstTable(table_base):
    from sqlalchemy import Column, Integer, String, DateTime
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.mutable import MutableDict

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
