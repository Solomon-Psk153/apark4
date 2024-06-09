from flask_restful import Resource, reqparse
from flask import request
from DBClass import *
from FlaskAPP import app
import jwt

class UpdateUserStatus(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        if user.place not in ['admin', '관리자']:
            return {'message': 'Permission denied'}, 400
        
        parser = reqparse.RequestParser()
        parser.add_argument('userID', type=str, required=True, help='id must be string and necessary key')
        parser.add_argument('userStatus', type=str, required=True, help='device_info must be string and necessary key')
        args = parser.parse_args(strict=True)
        userID = args['userID']
        userStatus = args['userStatus']
        
        if userStatus not in ['active', 'dead', '활성', '정지']:
            return {'message': 'userStatus out of range'}, 400
        
        findUserID = User.query.filter( User.id == userID ).first()
        
        if not findUserID:
            return {'message': 'that user you find not found'}, 404

        try:
            
            findUserID.status = userStatus
            db.session.commit()
            return {'message': 'User status changed successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': f'server internal error{str(e)}'}, 500
            
        finally:
            db.session.close()