## quiz_backend/applications/api.py
from flask import request, jsonify
from flask_restful import Resource


class HelloAPI(Resource):
    def get(self):
        return {'message': 'Hello from Quiz App!'}, 200