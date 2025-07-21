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
    def put(self, question_id):
        current_user = get_jwt_identity()
        data = request.get_json()
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question not found.'}, 404

        if 'question_statement' in data and data['question_statement'].strip():
            question.question_statement = data['question_statement'].strip()

        if 'option1' in data and data['option1'].strip():
            question.option1 = data['option1'].strip()

        if 'option2' in data and data['option2'].strip():
            question.option2 = data['option2'].strip()

        if 'option3' in data and data['option3'].strip():
            question.option3 = data['option3'].strip()

        if 'option4' in data and data['option4'].strip():
            question.option4 = data['option4'].strip()

        if 'correct_option' in data and data['correct_option'].strip():
            question.correct_option = data['correct_option'].strip()

        if 'quiz_id' in data:
            question.quiz_id = data['quiz_id']

        if 'master_id' in data:
            question.master_id = data['master_id']

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