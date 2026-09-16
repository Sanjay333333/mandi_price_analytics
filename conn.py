from sqlalchemy import create_engine
from sqlalchemy.engine import URL

connection_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="password",
    host="localhost",
    port=4444,
    database="AGRI"
)

engine = create_engine(connection_url)