from flask import request,jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from applications.models import db, Quiz, QuizAttempt, Chapter, Question, QuizAttemptAnswer, User
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo 
from sqlalchemy.orm import joinedload
from applications.quiz_task_api import schedule_quiz_submission  
from applications.quiz_task_api import data_export


def get_current_user():
    return get_jwt_identity()

def get_user_role():
    return get_jwt().get("role")

class QuizAPI(Resource):
    @jwt_required()
    def get(self):
        chapter_id = request.args.get('chapter_id', type=int)

        query = Quiz.query.options(joinedload(Quiz.questions))  # eager load questions

        if chapter_id is not None:
            query = query.filter_by(chapter_id=chapter_id)

        quizzes = query.all()
        if not quizzes:
            return {'message': 'No quizzes found.'}, 404

        return {
            'quizzes': [
                {
                    **quiz.convert_to_json(),
                    'questions': [
                        {
                            'id': q.id,
                            'text': q.question_statement,
                            'options': [q.option1, q.option2, q.option3, q.option4]
                        }
                        for q in quiz.questions
                    ]
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

        # Field updates with validation
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

        # 🔔 Schedule Celery task to auto-submit
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
class QuizFeedbackAPI(Resource):
    @jwt_required()
    def post(self, quiz_id):
        user_id = get_current_user()
        user_role = get_user_role()
        
        if user_role != 'student':
            return {'message': 'Only students can submit feedback.'}, 403

        attempt = QuizAttempt.query.filter_by(student_id=user_id, quiz_id=quiz_id).first()

        if not attempt:
            return {'message': 'Quiz attempt not found.'}, 404

        # Prevent multiple feedback submissions
        if attempt.remarks:
            return {'message': 'Feedback already submitted.'}, 400

        data = request.get_json()
        remarks = data.get('remarks')

        if not remarks:
            return {'message': 'Remarks field is required.'}, 400

        attempt.remarks = remarks
        db.session.commit()

        return {'message': 'Feedback submitted successfully.'}, 200
    
class QuizFeedbackViewAPI(Resource):
    @jwt_required()
    def get(self, quiz_id):
        user_id = get_current_user()
        user_role = get_user_role()

        if user_role != 'quiz_master':
            return {'message': 'Only quiz masters can view feedback.'}, 403

        if quiz_id == 0:
            # Get all quizzes created by the quiz master
            quizzes = Quiz.query.filter_by(master_id=user_id).all()
            quiz_ids = [q.id for q in quizzes]

            # Get all attempts with remarks for these quizzes
            attempts = QuizAttempt.query.filter(
                QuizAttempt.quiz_id.in_(quiz_ids),
                QuizAttempt.remarks != None
            ).options(joinedload(QuizAttempt.student)).all()
        else:
            quiz = Quiz.query.filter_by(id=quiz_id, master_id=user_id).first()
            if not quiz:
                return {'message': 'Quiz not found or not authorized.'}, 404

            attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).filter(
                QuizAttempt.remarks != None
            ).options(joinedload(QuizAttempt.student)).all()

        feedback_list = [
            {
                'student_id': attempt.student_id,
                'student_name': attempt.student.full_name if attempt.student else '',
                'remarks': attempt.remarks
            }
            for attempt in attempts
        ]

        return {'feedback': feedback_list}, 200
    

    
class SubmitQuizFeedbackAPI(Resource):
    @jwt_required()
    def patch(self, quiz_id):
        user_id = get_current_user()
        user_role = get_user_role()

        if user_role != 'student':
            return {'message': 'Only students can submit feedback.'}, 403

        data = request.get_json()
        remarks = data.get('remarks', '').strip()

        if not remarks:
            return {'message': 'Remarks cannot be empty.'}, 400

        # Get the student's quiz attempt
        attempt = QuizAttempt.query.filter_by(quiz_id=quiz_id, student_id=user_id).first()
        if not attempt:
            return {'message': 'Quiz attempt not found.'}, 404

        if not attempt.submitted:
            return {'message': 'Cannot give feedback before submitting the quiz.'}, 400

        # Fetch all submitted answers for the attempt
        submitted_answers = QuizAttemptAnswer.query.filter_by(attempt_id=attempt.id).all()

        # Recalculate the total score by comparing with correct answers
        total_score = 0
        for ans in submitted_answers:
            question = Question.query.get(ans.question_id)
            if question and ans.selected_option == question.correct_option:
                ans.is_correct = True
                total_score += 1
            else:
                ans.is_correct = False

        attempt.total_scored = total_score
        attempt.remarks = remarks
        db.session.commit()

        return {
            'message': 'Feedback and score updated successfully.',
            'score': total_score
        }, 200

    
class QuizScoreAPI(Resource):
    @jwt_required()
    def get(self, quiz_id):
        user_id = get_jwt_identity()
        current_user = get_jwt()

        if current_user.get('role') != 'student':
            return {'message': 'Only students can view their scores.'}, 403

        attempt = QuizAttempt.query.filter_by(student_id=user_id, quiz_id=quiz_id).first()
        if not attempt:
            return {'message': 'You have not started this quiz.'}, 404

        return {
            'quiz_id': quiz_id,
            'student_id': user_id,
            'start_time': attempt.quiz.start_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.quiz.start_time else None,
            'end_time': attempt.quiz.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.quiz.end_time else None,
            'submitted': attempt.submitted,
            'total_scored': attempt.total_scored,
            'score_recorded': attempt.total_scored is not None
        }, 200

    @jwt_required()
    def post(self, quiz_id):
        user_id = get_jwt_identity()
        current_user = get_jwt()

        if current_user.get('role') != 'student':
            return {'message': 'Only students can submit scores.'}, 403

        attempt = QuizAttempt.query.filter_by(student_id=user_id, quiz_id=quiz_id).first()
        if not attempt:
            return {'message': 'You must start the quiz before submitting answers.'}, 400

        if attempt.submitted:
            return {'message': 'You have already submitted this quiz.'}, 400

        now = datetime.now()
        quiz = attempt.quiz
        current_time = now.time()
        if now.date() != quiz.date_of_quiz or current_time > quiz.end_time:
            return {'message': 'Quiz submission time is over.'}, 403

        data = request.get_json()
        submitted_answers = data.get('answers')
        if not submitted_answers:
            return {'message': 'No answers submitted.'}, 400

        total_score = 0
        for question_id, student_answer in submitted_answers.items():
            question = Question.query.get(question_id)
            if question and question.correct_option == student_answer:
                total_score += 1

        attempt.total_scored = total_score
        attempt.submitted = True
        # If you want to store the time of submission, add `submitted_at = db.Column(db.DateTime)` to QuizAttempt

        db.session.commit()

        return {
            'message': 'Quiz score recorded successfully.',
            'total_scored': total_score
        }, 201

class QuizExportEmailAPI(Resource):
    @jwt_required()
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

        # ✅ Trigger async export via Celery
        data_export.delay(data=data, email=student.username)

        return {"message": "Export initiated. You’ll receive it via email shortly."}, 202