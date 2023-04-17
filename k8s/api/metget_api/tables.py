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
