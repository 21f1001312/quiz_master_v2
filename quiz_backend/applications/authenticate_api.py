## quiz_backend/applications/authenticateapi.py
from flask import request, jsonify
from flask import current_app as app
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask_jwt_extended import jwt_required
from applications.models import db, User
from datetime import datetime
class AuthAPI(Resource):
    def post(self):
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return {'message': 'Both username and password are required.'}, 400

        user = User.query.filter_by(username=data.get('username')).first()
        if user:
            if user.password == data.get('password'):
                if user.role == 'student' and user.status == 'pending':
                    return {'message': 'Student account is pending.'}, 403

                token = create_access_token(
                    identity=str(user.id),
                    additional_claims={"role": user.role}
                )
                return {
                    'message': 'User logged in successfully.',
                    'token': token,
                    'User_name': user.username,
                    'user_role': user.role
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

        if user.status == 'pending' and user.role == 'student':
            user.status = 'active'
            message = f'{user.role.capitalize()} account has been approved.'
        elif user.status == 'active':
            user.status = 'blocked'
            message = f'{user.role.capitalize()} account has been blocked.'
        elif user.status == 'blocked':
            user.status = 'active'
            message = f'{user.role.capitalize()} account has been unblocked.'
        else:
            return {'message': f'Unhandled status: {user.status}'}, 400

        db.session.commit()
        return {'message': message, 'new_status': user.status}, 200

    @jwt_required()
    def delete(self, user_id):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'User not found.'}, 404

        if user.role != 'student':
            return {'message': 'Only student accounts can be deleted.'}, 403

        db.session.delete(user)
        db.session.commit()
        return {'message': 'Student deleted successfully.'}, 200


class StudentAPI(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        students = User.query.filter_by(role='student').all()
        data = [student.convert_to_json() for student in students]
        return {'students': data}, 200
    

class SignupAPI(Resource):
    def post(self):
        data = request.get_json()

        required_fields = ['username', 'password', 'full_name', 'qualification', 'date_of_birth']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return {'message': f"Missing fields: {', '.join(missing_fields)}"}, 400

        username = data['username'].strip()
        password = data['password'].strip()
        full_name = data['full_name'].strip()
        qualification = data['qualification'].strip()
        dob_str = data['date_of_birth'].strip()

        if len(full_name) < 3 or len(full_name) > 100:
            return {'message': 'Full name must be between 4 and 100 characters.'}, 400

        if len(username) > 120 or "@" not in username:
            return {'message': 'Username must be a valid email with less than 121 characters.'}, 400

        if len(password) < 4 or len(password) > 20:
            return {'message': 'Password must be between 4 and 20 characters.'}, 400

        try:
            date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Date of birth must be in YYYY-MM-DD format.'}, 400

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {'message': 'User already exists with this email.'}, 400

        new_student = User(
            username=username,
            password=password,
            full_name=full_name,
            qualification=qualification,
            date_of_birth=date_of_birth,
            role='student',
            status='pending' 
        )

        db.session.add(new_student)
        db.session.commit()

        return {
            'message': 'Student account created successfully. Awaiting approval by Quiz Master.'
        }, 201