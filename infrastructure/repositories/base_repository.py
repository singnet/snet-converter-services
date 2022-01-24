from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

from config import NETWORK
from utils.database import update_in_db

driver = NETWORK['db']['DB_DRIVER']
host = NETWORK['db']['DB_HOST']
user = NETWORK['db']["DB_USER"]
db_name = NETWORK['db']["DB_NAME"]
password = NETWORK['db']["DB_PASSWORD"]
port = NETWORK['db']["DB_PORT"]
db_logging = NETWORK['db']["DB_LOGGING"]

connection_string = f"{driver}://{user}:{password}@{host}:{port}/{db_name}"
engine = create_engine(connection_string, pool_pre_ping=True, echo=db_logging)

Session = sessionmaker(bind=engine)
default_session = Session()


class BaseRepository:
    def __init__(self):
        self.session = default_session

    @update_in_db()
    def add_item(self, item):
        self.session.add(item)

    @update_in_db()
    def add_all_items(self, items):
        self.session.add_all(items)
