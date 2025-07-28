from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from applications.models import Subject, Chapter, Quiz, Question, QuizAttempt, User

class MastereoSearchAPI(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get("q", "").strip().lower()
        if not query:
            return {"error": "Query string cannot be empty"}, 400
        
        # Search Students
        students = User.query.filter(User.username.ilike(f"%{query}%")).all()
        student_results = [{
            "id": s.id,
            "username": s.username
        } for s in students]

        # Search Subjects
        subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        subject_results = [{
            "id": s.id,
            "name": s.name
        } for s in subjects]

        # Search Quizzes
        quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
        quiz_results = [{
            "id": q.id,
            "title": q.title,
            "chapter_id": q.chapter_id,
            "date_of_quiz": q.date_of_quiz.strftime('%Y-%m-%d') if q.date_of_quiz else None
        } for q in quizzes]

        return {
            "students": student_results,
            "subjects": subject_results,
            "quizzes": quiz_results
        }, 200


class StudentSearchAPI(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get("q", "").strip().lower()
        if not query:
            return {"error": "Query string cannot be empty"}, 400

        student_id = get_jwt_identity()
        student = User.query.get(student_id)

        if not student:
            return {"error": "Student not found"}, 404

        # Get quiz IDs the student has attempted
        attempts = QuizAttempt.query.filter_by(student_id=student.id).all()
        quiz_ids = list(set(a.quiz_id for a in attempts))

        if not quiz_ids:
            return {"quizzes": []}, 200

        quizzes = Quiz.query.filter(
            Quiz.id.in_(quiz_ids),
            Quiz.title.ilike(f"%{query}%")
        ).all()

        quiz_results = [{
            "id": q.id,
            "title": q.title,
            "chapter_id": q.chapter_id,
            "date_of_quiz": q.date_of_quiz.strftime('%Y-%m-%d') if q.date_of_quiz else None
        } for q in quizzes]

        return {"quizzes": quiz_results}, 200
