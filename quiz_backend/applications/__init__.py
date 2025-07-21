# quiz_backend/applications/__init__.py
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from datetime import date

from applications.config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
api = Api(app)
jwt = JWTManager(app)
CORS(app)

app.app_context().push()

from applications.models import User
from applications.authenticate_api import SignupAPI, AuthAPI, StudentAPI
from applications.subject_api import SubjectAPI, SubjectByIdAPI
from applications.chapter_api import ChapterAPI, ChapterByIdAPI
from applications.quiz_api import QuizAPI, QuizByIdAPI, QuizFeedbackAPI
from applications.question_api import QuestionAPI, QuestionByIdAPI
from applications.start_quiz_api import StartQuizAPI


with app.app_context():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")

    if not os.path.exists(db_path):
        db.create_all()
        print(" Database created.")

        admin = User.query.filter_by(username='admin@gmail.com').first()
        if not admin:
            admin = User(
                username='admin@gmail.com',
                password='admin123',
                full_name='Quiz Master',
                qualification='M.Sc. Computer Science',
                date_of_birth=date(1990, 1, 1),  
                role='quiz_master',
                status='approved'
            )
            db.session.add(admin)
            db.session.commit()
            print(" Quiz Master added.")


api.add_resource(SignupAPI, '/api/signup')
api.add_resource(AuthAPI, '/api/login', '/api/approve/<int:user_id>', '/api/delete/<int:user_id>')
api.add_resource(StudentAPI, '/api/students')
api.add_resource(SubjectAPI, '/api/subjects')
api.add_resource(SubjectByIdAPI, '/api/subjects/<int:subject_id>')
api.add_resource(ChapterAPI, '/api/chapter', '/api/chapter/subject/<int:subject_id>')
api.add_resource(ChapterByIdAPI, '/api/chapter/<int:chapter_id>')
api.add_resource(QuizAPI, '/api/quiz')
api.add_resource(QuizByIdAPI, '/api/quiz/<int:quiz_id>')
api.add_resource(QuizFeedbackAPI, '/api/quiz/<int:quiz_id>/feedback')
api.add_resource(QuestionAPI, '/api/question')
api.add_resource(QuestionByIdAPI, '/api/question/<int:question_id>')
api.add_resource(StartQuizAPI, '/api/quiz/<int:quiz_id>/start')
