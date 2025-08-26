from config import config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


username = config.get("DB", "user")
password = config.get("DB", "password")
db_name = config.get("DB", "db_name")
domain = config.get("DB", "domain")
port = config.get("DB", "db_port")


#  f'postgresql://username:password@domain_name:port/database_name'

DB_CONNECTION_URL = f"postgresql://{username}:{password}@{domain}:{port}/{db_name}"

engine = create_engine(DB_CONNECTION_URL)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

