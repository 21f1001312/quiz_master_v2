## quiz_backend/applications/models.py
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

    # for quiz master
    # subjects = db.relationship('Subject', backref='creator', lazy=True, foreign_keys='Subject.master_id')
    # chapters = db.relationship('Chapter', backref='creator', lazy=True, foreign_keys='Chapter.master_id')
    # quizzes_created = db.relationship('Quiz', backref='creator', lazy=True, foreign_keys='Quiz.master_id')
    questionns = db.relationship('Question', backref='user', lazy=True)
    
    # for student
    scores = db.relationship('Score', backref='user', lazy=True)

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

    chapters = db.relationship('Chapter', backref='subject', lazy=True)

    def convert_to_json(self):
        return{
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

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

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

    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

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

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)

    total_scored = db.Column(db.Integer)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)


