## applications/models.py
from datetime import datetime
from applications import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(50), nullable=False, default='student')
    status = db.Column(db.String(50), nullable=False, default='active') 

    questionns = db.relationship('Question', backref='user', lazy=True, cascade="all, delete")
    scores = db.relationship('Score', backref='user', lazy=True, cascade="all, delete")

    def convert_to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'full_name': self.full_name,
            'qualification': self.qualification,
            'date_of_birth': self.date_of_birth.strftime('%Y-%m-%d') if self.date_of_birth else None,
            'role': self.role,
            'status': self.status
        }

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.Text)
    level = db.Column(db.String(50))

    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete")
    quizzes = db.relationship('Quiz', backref='subject', lazy=True, cascade="all, delete")

    def convert_to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level
        }

class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)  

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete")

    def convert_to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "subject_id": self.subject_id,
            "subject_name": self.subject.name,
            "subject_level": self.subject.level 
        }

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, default=10)

    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')

    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete")
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade="all, delete")

    def convert_to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "date_of_quiz": self.date_of_quiz.strftime('%Y-%m-%d') if self.date_of_quiz else None,
            "duration_minutes": self.duration_minutes,
            "remarks": self.remarks,
            "status": self.status,
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M') if self.start_time else None,
            "end_time": self.end_time.strftime('%Y-%m-%d %H:%M') if self.end_time else None,
            "subject_name": self.subject.name,
            "chapter_name": self.chapter.name
        }

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True) 

    question_statement = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 

    def convert_to_json(self):
        return {
            "id": self.id,
            "question_statement": self.question_statement,
            "option1": self.option1,
            "option2": self.option2,
            "option3": self.option3,
            "option4": self.option4,
            "correct_option": self.correct_option,
            "quiz_id": self.quiz_id,
            "master_id": self.master_id
        }

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)

    total_scored = db.Column(db.Integer)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)

    def convert_to_json(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "quiz_id": self.quiz_id,
            "total_scored": self.total_scored,
            "time_stamp_of_attempt": self.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S') if self.time_stamp_of_attempt else None
        }
