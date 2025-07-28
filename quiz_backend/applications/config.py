# quiz_backend/applications/config.py
import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'database.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '1234'

    # JWT config
    JWT_SECRET_KEY = '12345678'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    # Flask-Caching (Redis)
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TIMEZONE = 'Asia/Kolkata'
    CELERY_ENABLE_UTC = False