## quiz_backend/applications/__init__.py
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

from applications.config import Config
from applications.models import User
from applications.authenticate_api import AuthAPI, StudentAPI

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    api = Api(app)
    api.add_resource(AuthAPI, '/api/login', '/api/approve/<int:user_id>', '/api/delete/<int:user_id>')
    api.add_resource(StudentAPI, '/api/students')

    app.app_context().push()

    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.sqlite3')
    if not os.path.exists(db_path):
        db.create_all()
        print("📦 Database created.")

    quiz_master = User.query.filter_by(username='admin@gmail.com').first()
    if not quiz_master:
        quiz_master = User(
            username='admin@gmail.com',
            password='admin123',
            full_name='Quiz Master',
            qualification='Master of Quizzes',
            is_quiz_master=True
        )
        db.session.add(quiz_master)
        db.session.commit()
        print("✅ Default quiz master created.")

    return app
