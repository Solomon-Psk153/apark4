from flask_restful import Resource, reqparse
from FlaskAPP import app
from DBClass import User, UserSchema
import hashlib, jwt
from flask import request
from FunctionClass import *

class Login(Resource):
    
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='id must be string and necessary key')
        parser.add_argument('passwd', type=str, required=True, help='passwd must be string and necessary key')
        parser.add_argument('device_info', type=str, required=True, help='device_info must be string and necessary key')
        args = parser.parse_args(strict=True)
        userID = args['id']
        passwd = args['passwd']
        device_info = args['device_info']
        
        user = User.query.filter_by(
                id=userID, 
                passwd=createHash(passwd, addSalt=True)
            ).first()
        
        if user is None:
            return {'message': 'invalid credentials'}, 401
        
        else:
            token = request.headers.get('Authorization')
            if token:
                try:
                    decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                    validUserEmail = decoded['email']
                    
                    # 기존 토큰이 유효하고, 이메일이 일치하면 새 토큰 발급
                    if user.email == validUserEmail:
                        token = generateToken(userID, user.email, device_info)
                        return {'message': 'Token refreshed', 'token': token}, 200
                    
                    # 토큰이 유효하지만 이메일이 일치하지 않으면 오류 반환
                    return {'message': 'User Email in Token not match in Server'}, 400

                    
                except jwt.ExpiredSignatureError:
                    pass  # 토큰이 만료된 경우 새로 발급
                except jwt.InvalidTokenError:
                    pass  # 토큰이 유효하지 않은 경우 새로 발급
                
            
            token = generateToken(userID, user.email, device_info)
            return {'message': token}, 200
    
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response