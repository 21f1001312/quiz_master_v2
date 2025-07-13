## quiz_backend/applications/authenticateapi.py
from flask import request, jsonify
from flask import current_app as app
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask_jwt_extended import jwt_required
from applications.models import db, User

class AuthAPI(Resource):
    def post(self):
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return {'message': 'Both email and password are required.'}, 400

        user = User.query.filter_by(username=data.get('email')).first()
        if user:
            if user.password == data.get('password'):
                token = create_access_token(
                    identity=str(user.id),
                    additional_claims={"role": "quiz_master" if user.is_quiz_master else "student"}
                )
                return {
                    'message': 'User logged in successfully.',
                    'token': token,
                    'username': user.username,
                    'is_quiz_master': user.is_quiz_master
                }, 200
            return {'message': 'Invalid password.'}, 400
        return {'message': 'User not found.'}, 404

    @jwt_required()
    def patch(self, user_id):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'User not found.'}, 404

        user.is_quiz_master = not user.is_quiz_master
        db.session.commit()
        return {'message': 'Quiz master role toggled.', 'new_status': user.is_quiz_master}, 200

    @jwt_required()
    def delete(self, user_id):
        current_user = get_jwt()
        if current_user.get('role') != 'admin':
            return {'message': 'Access Denied'}, 403

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'User not found.'}, 404

        if user.is_quiz_master:
            return {'message': 'Cannot delete quiz master.'}, 403

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully.'}, 200


class StudentAPI(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        students = User.query.filter_by(is_quiz_master=False).all()
        data = [student.convert_to_json() for student in students]
        return {'students': data}, 200
    
class SignupAPI(Resource):
    def post(self):
        data = request.get_json()

        # Basic field validation
        if not data.get('username') or not data.get('password') or not data.get('full_name'):
            return {'message': 'Username (email), password, and full name are required.'}, 400

        if len(data['full_name'].strip()) < 4 or len(data['full_name'].strip()) > 100:
            return {'message': 'Full name must be between 4 and 100 characters.'}, 400

        if len(data['username'].strip()) > 120 or "@" not in data['username']:
            return {'message': 'Username must be a valid email with less than 121 characters.'}, 400

        if len(data['password'].strip()) < 4 or len(data['password'].strip()) > 20:
            return {'message': 'Password must be between 4 and 20 characters.'}, 400

        # Role must only be student for signup
        if data.get('role', '').strip().lower() != 'student':
            return {'message': 'Only students can sign up. Quiz masters are created by admin.'}, 403

        existing_user = User.query.filter_by(username=data['username'].strip()).first()
        if existing_user:
            return {'message': 'User already exists with this email.'}, 400

        new_student = User(
            username=data['username'].strip(),
            password=data['password'].strip(),
            full_name=data['full_name'].strip(),
            role='student',
            status='pending',  
            is_quiz_master=False
        )

        db.session.add(new_student)
        db.session.commit()

        return {'message': 'Student account created. Awaiting approval by Quiz Master.'}, 201
