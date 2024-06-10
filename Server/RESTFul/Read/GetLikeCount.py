from flask_restful import Resource, reqparse
from flask import request
from DBClass import *
from FlaskAPP import app
from FunctionClass import *
import jwt

class GetLikeCount(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        parser = reqparse.RequestParser()
        parser.add_argument('hash', type=str, required=True, help='hash must be string and necessary key')
        
        args = parser.parse_args(strict=True)
        
        hash = args['hash']
        
        writing = Writing.query.filter( Writing.hash == hash ).first()
        
        if writing is None:
            return {'message': 'Writing not found'}, 404
        
        writingLikeCount = WritingLike.query.filter( WritingLike.whichWriting == writing.hash ).count()
        
        print(writingLikeCount)
        
        return {'message': writingLikeCount}, 200