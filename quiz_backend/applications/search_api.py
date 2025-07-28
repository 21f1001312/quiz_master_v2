from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from applications.models import Subject, User

# Quiz Master searches for STUDENTS only
class MastereoSearchAPI(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get("q", "").strip().lower()
        if not query:
            return {"error": "Query string cannot be empty"}, 400

        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or user.role != "quiz_master":
            return {"error": "Access denied. Only quiz masters can search here."}, 403

        students = User.query.filter(
            User.role == "student",
            User.username.ilike(f"%{query}%")
        ).all()
        student_results = [{"id": s.id, "username": s.username} for s in students]

        return {"students": student_results}, 200


# Student searches for SUBJECTS only
class StudentSearchAPI(Resource):
    @jwt_required()
    def get(self):
        query = request.args.get("q", "").strip().lower()
        if not query:
            return {"error": "Query string cannot be empty"}, 400

        student_id = get_jwt_identity()
        student = User.query.get(student_id)

        if not student or student.role != "student":
            return {"error": "Access denied. Only students can search here."}, 403

        subjects = Subject.query.filter(
            Subject.name.ilike(f"%{query}%")
        ).all()
        subject_results = [{"id": s.id, "name": s.name} for s in subjects]

        return {"subjects": subject_results}, 200
