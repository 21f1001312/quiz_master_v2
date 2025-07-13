from datetime import datetime
from applications import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)  # Email
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(50), nullable=False, default='student')
    status = db.Column(db.String(50), nullable=False, default='active') 

    subjects = db.relationship('Subject', backref='creator', lazy=True)
    chapters = db.relationship('Chapter', backref='creator', lazy=True)
    quizzes = db.relationship('Quiz', backref='creator', lazy=True)
    questions = db.relationship('Question', backref='creator', lazy=True)
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
    status = db.Column(db.String(20), default='active')
    level = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Creator (quiz master)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)

class Chapter(db.Model):
    __tablename__ = 'chapters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Creator (quiz master)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)

    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Creator (quiz master)

    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, default=10)

    remarks = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')

    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    questions = db.relationship('Question', backref='quiz', lazy=True)
    scores = db.relationship('Score', backref='quiz', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Creator (quiz master)

    question_statement = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)

    total_scored = db.Column(db.Integer)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
