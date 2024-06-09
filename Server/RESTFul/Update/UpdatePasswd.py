from flask_restful import Resource, reqparse
from flask import request
from FlaskAPP import app
from DBClass import User, UserSchema, db
from FunctionClass import createHash
import jwt

class UpdatePasswd(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('myInputPasswd', type=str, required=True, help='myInputPasswd must be string and necessary key')
        parser.add_argument('newPasswd', type=str, required=True, help='newPasswd must be string and necessary key')
        args = parser.parse_args(strict=True)
        myInputPasswd = createHash(args['myInputPasswd'], addSalt=True)
        newPasswd = args['newPasswd']
        
        if user.passwd != myInputPasswd:
            return {'message': 'input passwd not match'}, 400
        
        try:
            user.passwd = createHash(newPasswd, addSalt=True)
            db.session.commit()
            return {'message': 'user passwd successfully updated'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': 'Error creating user: {}'.format(e)}, 500
        
        finally:
            db.session.close()
        