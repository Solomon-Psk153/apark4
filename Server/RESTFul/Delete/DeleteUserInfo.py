from flask_restful import Resource, reqparse
from flask import request
import jwt
from FlaskAPP import app
from DBClass import *
from FunctionClass import createHash

class DeleteUserInfo(Resource):
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        parser = reqparse.RequestParser()
        parser.add_argument('passwd', type=str, required=True, help='passwd must be string and necessary key')
        args = parser.parse_args(strict=True)
        
        user = User.query.filter( 
                    ( User.id==validUserID ), 
                    ( User.passwd==createHash(args['passwd'], addSalt=True) ) 
                ).first()
        
        if user is None:
            return {'message': 'id and passwd not match'}, 400

        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'user successfully deleted'}, 200
        
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': 'Error creating user: {}'.format(e)}, 500
        
        finally:
            db.session.close()