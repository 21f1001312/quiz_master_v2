from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from applications.models import db, Subject

class SubjectAPI(Resource):
    @jwt_required()
    def get(self):
        subjects = Subject.query.all()
        data = [sub.convert_to_json() for sub in subjects]
        return {'subjects': data}, 200
    
    @jwt_required()
    def post(self):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403
        
        data = request.get_json()
        if not data.get('name'):
            return {'message': 'Category name is required.'}, 400
        
        if len(data.get('name').strip()) > 81 or len(data.get('name').strip()) < 4:
            return {'message': 'Category name must be between 4-80 characters.'}, 400
        
        if not data.get('description'):
            return {'message': 'Category description is required.'}, 400
        
        if not data.get('level'):
            return {'message': 'Category level is required.'}, 400
        
        new_subject = Subject(name=data.get('name').strip(), 
                              description=data.get('description').strip(),
                              level=data.get('level').strip())
        
        db.session.add(new_subject)
        db.session.commit()

        return {'message': 'Subject created successfully.'}, 200
    
    @jwt_required()
    def put(self, subject_id):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        data = request.get_json()
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject not found.'}, 404

        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 3 or len(name) > 80:
                return {'message': 'Subject name must be between 4-80 characters.'}, 400
            subject.name = name

        if 'description' in data:
            subject.description = data['description'].strip()

        if 'level' in data:
            subject.level = data['level'].strip()

        db.session.commit()
        return {'message': 'Subject updated successfully.'}, 200

    
    @jwt_required()
    def delete(self, subject_id):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403
        
        subject = Subject.query.get(subject_id)
        if not subject:
            return {'message': 'Subject not found.'}, 404
        
        db.session.delete(subject)
        db.session.commit()
        
        return {'message': 'Subject deleted successfully.'}, 200