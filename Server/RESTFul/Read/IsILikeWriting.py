from flask_restful import Resource, reqparse
from flask import request
from DBClass import *
from FlaskAPP import app
import jwt

class IsILikeWriting(Resource):
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        parser = reqparse.RequestParser()
        parser.add_argument('hash', type=str, required=True, help='hash must be string and necessary key')
        
        args = parser.parse_args(strict=True)
        
        hash = args['hash']
        
        writing = Writing.query.filter( Writing.hash == hash ).first()
        
        if writing is None:
            return {'message': 'Writing not found'}, 404
        
        isILike = WritingLike.query.filter( (WritingLike.whichWriting == writing.hash), ( WritingLike.userID == user.id ) ).first()
        
        if isILike is None:
            return {'message': 'no'}, 200
        
        else:
            return {'message': 'yes'}, 200