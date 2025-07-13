from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from applications.models import db, Chapter, Subject

class ChapterAPI(Resource):
    @jwt_required()
    def get(self, chapter_id=None, subject_id=None):
        if chapter_id:
            chapter = Chapter.query.get(chapter_id)
            if not chapter:
                return {'message': 'Chapter not found'}, 404
            return chapter.convert_to_json(), 200

        if subject_id:
            chapters = Chapter.query.filter_by(subject_id=subject_id).all()
            if not chapters:
                return {'message': f'No chapters found for subject ID {subject_id}'}, 404
            return {'chapters': [chapter.convert_to_json() for chapter in chapters]}, 200

        # default: return all chapters
        chapters = Chapter.query.all()
        return {'chapters': [chapter.convert_to_json() for chapter in chapters]}, 200

    
    @jwt_required()
    def post(self):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403

        data = request.get_json()

        # Validate required fields
        if not (data.get('name') and data.get('description') and data.get('subject_id')):
            return {'message': 'All fields (name, description, subject_id) are required.'}, 400

        name = data.get('name').strip()
        if len(name) < 4 or len(name) > 80:
            return {'message': 'Chapter name must be between 4-80 characters.'}, 400

        subject = Subject.query.get(data.get('subject_id'))
        if not subject:
            return {'message': 'Subject not found.'}, 404

        new_chapter = Chapter(
            name=name,
            description=data.get('description').strip(),
            subject_id=data.get('subject_id')
        )

        db.session.add(new_chapter)
        db.session.commit()
        return {'message': 'Chapter created successfully.'}, 200
    
    @jwt_required()
    def put(self, chapter_id):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403
        
        data = request.get_json()
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return {'message': 'Chapter not found.'}, 404
        
        if 'name' in data:
            name = data['name'].strip()
            if len(name) < 3 or len(name) > 80:
                return {'message': 'Chapter name must be between 4-80 characters.'}, 400
            chapter.name = name
        
        if 'description' in data:
            chapter.description = data['description'].strip()
        
        db.session.commit()
        return {'message': 'Chapter updated successfully.'}, 200
    
    @jwt_required()
    def delete(self, chapter_id):
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403
        
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return {'message': 'Chapter not found.'}, 404
        
        db.session.delete(chapter)
        db.session.commit()
        return {'message': 'Chapter deleted successfully.'}, 200
        

       
    
    