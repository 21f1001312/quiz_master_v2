from flask import request,jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from applications.models import db, Quiz, QuizAttempt, Chapter, Question, QuizAttemptAnswer, User
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo 
from sqlalchemy.orm import joinedload
from applications.quiz_task_api import schedule_quiz_submission  
from applications.quiz_task_api import data_export
from applications.cache import cache


def get_current_user():
    return get_jwt_identity()

def get_user_role():
    return get_jwt().get("role")

class QuizAPI(Resource):
    @jwt_required()
    def get(self):
        chapter_id = request.args.get('chapter_id', type=int)
        student_id = get_jwt_identity()
        query = Quiz.query.options(joinedload(Quiz.questions))
        if chapter_id is not None:
            query = query.filter_by(chapter_id=chapter_id)
        quizzes = query.all()
        if not quizzes:
            return {'message': 'No quizzes found.'}, 404

        return {
            'quizzes': [
                {
                    **quiz.convert_to_json(),
                    'scores': (
                        QuizAttempt.query.filter_by(student_id=student_id, quiz_id=quiz.id, submitted=True)
                        .first().total_scored
                        if QuizAttempt.query.filter_by(student_id=student_id, quiz_id=quiz.id, submitted=True).first()
                        else None
                    ),
                    'submitted': bool(
                        QuizAttempt.query.filter_by(student_id=student_id, quiz_id=quiz.id, submitted=True).first()
                    ),
                    
                }
                for quiz in quizzes
            ]
        }, 200


    @jwt_required()
    def post(self):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        data = request.get_json()

        required_fields = ['title', 'date_of_quiz', 'start_time', 'time_duration', 'chapter_id']
        for field in required_fields:
            if not data.get(field):
                return {'message': f'{field.replace("_", " ").capitalize()} is required.'}, 400

        # Validate chapter
        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return {'message': 'Chapter not found.'}, 404

        try:
            # Parse date
            date_of_quiz = datetime.strptime(data['date_of_quiz'], '%Y-%m-%d').date()

            # Parse start_time as datetime.datetime using a dummy date
            start_dt = datetime.strptime(data['start_time'], '%H:%M')

            # Add time duration
            end_dt = start_dt + timedelta(minutes=data['time_duration'])

            # Extract only the time part
            start_time = start_dt.time()
            end_time = end_dt.time()

        except ValueError:
            return {'message': 'Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time.'}, 400

        current_user_id = get_jwt_identity()

        new_quiz = Quiz(
            title=data['title'].strip(),
            date_of_quiz=date_of_quiz,
            start_time=start_time,
            end_time=end_time,
            time_duration=data['time_duration'],
            subject_id=chapter.subject_id,
            chapter_id=chapter.id,
            master_id=current_user_id,
            status= 'scheduled'
        )

        db.session.add(new_quiz)
        db.session.commit()

        return {'message': 'Quiz created successfully.'}, 201

    
class QuizByIdAPI(Resource):
    @jwt_required()
    def get(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found.'}, 404
        return quiz.convert_to_json(), 200

    @jwt_required()
    def put(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found.'}, 404

        data = request.get_json()

        if 'title' in data and data['title'].strip():
            quiz.title = data['title'].strip()

        if 'date_of_quiz' in data:
            try:
                quiz.date_of_quiz = datetime.strptime(data['date_of_quiz'], '%Y-%m-%d').date()
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

        if 'start_time' in data:
            try:
                quiz.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            except ValueError:
                return {'message': 'Invalid time format. Use HH:MM.'}, 400

        if 'duration_minutes' in data:
            quiz.duration_minutes = data['duration_minutes']

        db.session.commit()
        return {'message': 'Quiz updated successfully.', 'quiz': quiz.convert_to_json()}, 200

    @jwt_required()
    def delete(self, quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found.'}, 404

        db.session.delete(quiz)
        db.session.commit()
        return {'message': 'Quiz deleted successfully.'}, 200
    

class StartQuizAPI(Resource):
    @jwt_required()
    def post(self, quiz_id):
        current_user_id = get_jwt_identity()

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {"message": "Quiz not found"}, 404

        existing_attempt = QuizAttempt.query.filter_by(
            student_id=current_user_id, quiz_id=quiz_id
        ).first()

        if not existing_attempt:
            attempt = QuizAttempt(student_id=current_user_id, quiz_id=quiz_id)
            db.session.add(attempt)
            db.session.commit()
        else:
            attempt = existing_attempt

        # Schedule Celery task to auto-submit
        from datetime import timedelta
        delay = timedelta(minutes=quiz.time_duration)

        schedule_quiz_submission.apply_async(
            args=[attempt.id],
            countdown=delay.total_seconds()
        )

        return {
            "attempt_id": attempt.id,
            "quiz_id": quiz_id,
            "message": "Quiz attempt started. Timer has begun.",
        }, 200


class SubmitQuizAPI(Resource):
    @jwt_required()
    def post(self, quiz_id):
        user_id = get_jwt_identity()
        data = request.get_json()
        answers = data.get('answers', [])
        remarks = data.get('remarks', '')

        # Check if attempt already exists
        attempt = QuizAttempt.query.filter_by(student_id=user_id, quiz_id=quiz_id).first()
        if not attempt:
            attempt = QuizAttempt(student_id=user_id, quiz_id=quiz_id, submitted=True)
            db.session.add(attempt)
            db.session.commit()

        total_score = 0
        for ans in answers:
            question_id = ans['question_id']
            selected_option = ans['selected_option']

            question = Question.query.get(question_id)
            is_correct = question and (question.correct_option == selected_option)
            total_score += int(is_correct)

            attempt_answer = QuizAttemptAnswer(
                attempt_id=attempt.id,
                question_id=question_id,
                selected_option=selected_option,
                is_correct=is_correct,
                quiz_id=quiz_id
            )
            db.session.add(attempt_answer)

        attempt.total_scored = total_score
        attempt.submitted = True
        db.session.commit()

        return {
            'message': 'Quiz submitted successfully',
            'total_score': total_score,
            'remarks': remarks
        }, 200

    @jwt_required()
    def get(self, quiz_id):
        user_id = get_jwt_identity()

        attempt = QuizAttempt.query.filter_by(student_id=user_id, quiz_id=quiz_id).first()
        if not attempt:
            return {'message': 'No attempt found for this quiz'}, 404

        answers = QuizAttemptAnswer.query.filter_by(attempt_id=attempt.id).all()

        score = 0
        response = []
        for ans in answers:
            question = Question.query.get(ans.question_id)
            is_correct = question and (ans.selected_option == question.correct_option)
            score += int(is_correct)

            response.append({
                'question_id': ans.question_id,
                'selected_option': ans.selected_option,
                'correct_option': question.correct_option if question else None,
                'is_correct': is_correct
            })

        return {
            'quiz_id': quiz_id,
            'total_questions': len(answers),
            'correct_answers': score,
            'score_percentage': round((score / len(answers)) * 100, 2) if answers else 0,
            'answers': response
        }, 200
    

class QuizExportEmailAPI(Resource):
    @jwt_required()
    @cache.cached(timeout=60)
    def post(self):
        student_id = get_jwt_identity()
        student = User.query.get(student_id)
        if not student:
            return {"error": "User not found"}, 404

        attempts = QuizAttempt.query.filter_by(student_id=student.id).all()

        data = []
        for a in attempts:
            quiz = Quiz.query.get(a.quiz_id)
            if quiz:
                data.append({
                    "Quiz Title": quiz.title,
                    "Date": quiz.date_of_quiz.strftime('%Y-%m-%d'),
                    "Score": a.total_scored or 0,
                    "Status": "Submitted" if a.submitted else "Not Submitted"
                })
        data_export.delay(data=data, email=student.username)

        return {"message": "Export initiated. You’ll receive it via email shortly."}, 202