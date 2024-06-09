from flask_restful import Resource, reqparse
from DBClass import User, UserSchema
import jwt
from flask import request
from FlaskAPP import app

class GetUserProfileInfo(Resource):
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        return {'message': UserSchema().dump(user)}, 200