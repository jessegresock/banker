import os
from dotenv import load_dotenv


class Config:
    load_dotenv('/home/jgresoc/postgres.env')

    PG_HOST = os.getenv("POSTGRES_HOST")
    PG_PORT = os.getenv("POSTGRES_PORT")
    PG_USER = os.getenv("POSTGRES_USER")
    PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    PG_DATABASE = os.getenv("POSTGRES_DB")
