from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask import request
from datetime import datetime, timedelta
from applications.models import db, Quiz

class StartQuizAPI(Resource):
    @jwt_required()
    def post(self, quiz_id):
        current_user = get_jwt()
        user_id = get_jwt_identity()

        if current_user.get('role') != 'student':
            return {'message': 'Only students can start the quiz.'}, 403

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found.'}, 404

        # Optional: check if the current user is allowed to start this quiz

        # Set start and end times
        now = datetime.utcnow()
        quiz.start_time = now
        quiz.end_time = now + timedelta(minutes=quiz.duration_minutes)

        # Assign student_id to the quiz if not already set
        quiz.student_id = user_id

        db.session.commit()

        return {
            'message': 'Quiz started successfully.',
            'quiz_id': quiz.id,
            'start_time': quiz.start_time.isoformat(),
            'end_time': quiz.end_time.isoformat(),
            'duration_minutes': quiz.duration_minutes
        }, 200
