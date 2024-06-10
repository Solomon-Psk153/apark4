from flask_restful import Resource, reqparse
from flask import request
from FlaskAPP import app
from DBClass import User, UserSchema, db
from FunctionClass import createHash
from FunctionClass import *
import jwt

class UpdateNickname(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True, help='nickname must be string and necessary key')
        args = parser.parse_args(strict=True)
        nickname = args['nickname']
        
        try:
            user.nickname = nickname
            db.session.commit()
            return {'message': 'user nickname successfully updated'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating user: {}'.format(e)}, 500
        
        finally:
            db.session.close()
        