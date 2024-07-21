from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine

from packages.infra_config import config


class Base(DeclarativeBase):
    pass


db_engine = create_engine(config.get_db_dsn(), echo=False)
Base.metadata.create_all(db_engine)
Base.metadata.bind = db_engine
