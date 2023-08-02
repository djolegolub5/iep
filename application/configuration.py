import os;
from datetime import timedelta


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@shopDB/shop"
    JWT_SECRET_KEY = "JWTSecretDevKey"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
