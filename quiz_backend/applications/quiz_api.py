from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from applications.models import db, Quiz, Chapter, Subject
from datetime import datetime


class QuizAPI(Resource):
    @jwt_required()
    def get(self, quiz_id=None, chapter_id=None):
        if quiz_id:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return {'message': 'Quiz not found.'}, 404
            return quiz.convert_to_json(), 200
        
        if chapter_id:
            quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
            if not quizzes:
                return {'message': f'No quizzes found for chapter ID {chapter_id}'}, 404
            return {'quizzes': [quiz.convert_to_json() for quiz in quizzes]}, 200

        # default: return all quizzes
        quizzes = Quiz.query.all()
        return {'quizzes': [quiz.convert_to_json() for quiz in quizzes]}, 200
    
    
    from datetime import datetime

    @jwt_required()
    def post(self):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        data = request.get_json()

        # Individual field checks instead of list
        if not data.get('title'):
            return {'message': 'Title is required.'}, 400
        if not data.get('date_of_quiz'):
            return {'message': 'Date of quiz is required.'}, 400
        if not data.get('time_duration'):
            return {'message': 'Time duration is required.'}, 400
        if not data.get('duration_minutes'):
            return {'message': 'Duration (in minutes) is required.'}, 400
        if not data.get('chapter_id'):
            return {'message': 'Chapter ID is required.'}, 400

        # Validate chapter
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return {'message': 'Chapter not found.'}, 404

        # Convert date and time fields
        try:
            date_of_quiz = datetime.strptime(data['date_of_quiz'], '%Y-%m-%d').date()
            time_duration = datetime.strptime(data['time_duration'], '%H:%M:%S').time()
        except ValueError:
            return {'message': 'Invalid date or time format. Use YYYY-MM-DD and HH:MM:SS.'}, 400

        user_id = get_jwt_identity()

        # Create quiz instance
        new_quiz = Quiz(
            title=data['title'].strip(),
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            duration_minutes=data['duration_minutes'],
            remarks=data.get('remarks', '').strip(),
            subject_id=chapter.subject_id,
            chapter_id=chapter.id,
            master_id=user_id
        )

        db.session.add(new_quiz)
        db.session.commit()

        return {'message': 'Quiz created successfully.'}, 200

    @jwt_required()
    def put(self, quiz_id):
        data = request.get_json()
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found.'}, 404

        if 'title' in data:
            quiz.title = data['title'].strip()

        if 'date_of_quiz' in data:
            quiz.date_of_quiz = data['date_of_quiz']

        if 'time_duration' in data:
            quiz.time_duration = data['time_duration']

        if 'duration_minutes' in data:
            quiz.duration_minutes = data['duration_minutes']

        if 'remarks' in data:
            quiz.remarks = data['remarks'].strip()

        db.session.commit()
        return {'message': 'Quiz updated successfully.'}, 200
    
    @jwt_required()
    def delete(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found.'}, 404

        db.session.delete(quiz)
        db.session.commit()
        return {'message': 'Quiz deleted successfully.'}, 200