## quiz_backend/applications/config.py
import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'database.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '1234'
    JWT_SECRET_KEY = '12345678'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

