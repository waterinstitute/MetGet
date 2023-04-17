from sqlalchemy.orm import declarative_base
import enum

table_base = declarative_base()


class AuthTable(table_base):
    from sqlalchemy import Column, Integer, String, Boolean
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
    from sqlalchemy import Column, Integer, String, DateTime, Enum
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


class MetgetGenericMetadataTable(table_base):
    from sqlalchemy import Column, Integer, String, DateTime

    __tablename__ = "generic"

    index = Column("id", Integer, primary_key=True)
    forecastcycle = Column(DateTime)
    forecasttime = Column(DateTime)
    tau = Column(Integer)
    filepath = Column(String)
    url = Column(String)
    accessed = Column(DateTime)


class GfsTable(MetgetGenericMetadataTable):
    __tablename__ = "gfs_ncep"


class NamTable(MetgetGenericMetadataTable):
    __tablename__ = "nam_ncep"


class HwrfTable(MetgetGenericMetadataTable):
    from sqlalchemy import Column, String

    __tablename__ = "hwrf"
    stormname = Column(String)


class GefsTable(MetgetGenericMetadataTable):
    from sqlalchemy import Column, String

    __tablename__ = "gefs_fcst"
    ensemble_member = Column(String)


class CoampsTable(MetgetGenericMetadataTable):
    from sqlalchemy import Column, String

    __tablename__ = "coamps_tc"
    stormname = Column(String)


class HrrrTable(MetgetGenericMetadataTable):
    __tablename__ = "hrrr_ncep"


class HrrrAlaskaTable(MetgetGenericMetadataTable):
    __tablename__ = "hrrr_alaska_ncep"


class WpcTable(table_base):
    __tablename__ = "wpc_ncep"


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
