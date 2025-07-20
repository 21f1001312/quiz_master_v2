from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from applications.models import db, Question,Chapter, Quiz, Subject
from datetime import datetime

class QuestionAPI(Resource):
    @jwt_required()
    def get(self):
        chapter_id = request.args.get('chapter_id', type=int)
        if chapter_id is not None:
            questions = Question.query.filter_by(chapter_id=chapter_id).all()
            if not questions:
                return {'message': f'No questions found for chapter ID {chapter_id}'}, 404
            return {'questions': [question.convert_to_json() for question in questions]}, 200
        # Default: return all questions
        questions = Question.query.all()
        return {'questions': [question.convert_to_json() for question in questions]}, 200
    
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = get_jwt()
        if current_user.get('role') != 'quiz_master':
            return {'message': 'Access Denied'}, 403
        data = request.get_json()

        quiz_id = data.get('quiz_id')
        questions = data.get('questions')

        if not quiz_id or not questions or not isinstance(questions, list):
            return {'message': 'quiz_id and questions list are required'}, 400

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        # Add each question
        for q in questions:
            try:
                new_question = Question(
                    question_statement=q['question_statement'],
                    option1=q['option1'],
                    option2=q['option2'],
                    option3=q['option3'],
                    option4=q['option4'],
                    correct_option=q['correct_option'],
                    quiz_id=quiz_id,
                    master_id=current_user_id
                )
                db.session.add(new_question)
            except KeyError:
                return {'message': 'Each question must have all required fields'}, 400

        db.session.commit()
        return {'message': f'{len(questions)} questions added to quiz {quiz_id}'}, 201
    
class QuestionByIdAPI(Resource):
    @jwt_required()
    def get(self, question_id):
        current_user = get_jwt_identity()
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question not found.'}, 404
        return question.convert_to_json(), 200
    
    @jwt_required()
    def patch(self, question_id):
        current_user = get_jwt_identity()
        data = request.get_json()
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question not found.'}, 404
        for key, value in data.items():
            setattr(question, key, value)
        db.session.commit()
        return {'message': 'Question updated successfully.'}, 200
    
    @jwt_required()
    def delete(self, question_id):
        current_user = get_jwt_identity()
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question not found.'}, 404
        db.session.delete(question)
        db.session.commit()
        return {'message': 'Question deleted successfully.'}, 200