from flask_restful import Resource, reqparse
from flask import request
from DBClass import *
from FlaskAPP import app
import jwt

class UpdateUserStatus(Resource):
    
    def post(self):
        
        token = request.headers.get('Authorization')
        
        if not token:
            return {'message': 'Token is missing, Unauthorization'}, 401
        
        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            validUserID = decoded['id']
            validUserEmail = decoded['email']
            validDevice_info = decoded['device_info']
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
        
        request_device_info = request.headers.get('Device-Info')
        print("device_info:", validDevice_info, "\nDevice-Info:", request_device_info)
        if validDevice_info != request_device_info:
            return {'message': 'invalid device'}, 401
        
        user = User.query.filter_by( id=validUserID ).first()
        
        if user is None: # 토큰으로 사용자를 DB에서 찾았을 때, 존재하지 않음
            return {'message': 'User not Found'}, 404
        
        elif user.email != validUserEmail:
            return {'message': 'User Email in Token not match in Server'}, 400
        
        elif user.place not in ['admin', '관리자']:
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