from flask_restful import Resource, reqparse
from DBClass import User, UserSchema
import jwt
from flask import request
from FlaskAPP import app
from FunctionClass import *

class GetUserProfileInfo(Resource):
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        return {'message': UserSchema().dump(user)}, 200