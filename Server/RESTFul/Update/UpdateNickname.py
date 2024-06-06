from flask_restful import Resource, reqparse
from flask import request
from FlaskAPP import app
from DBClass import User, UserSchema, db
from FunctionClass import createHash
import jwt

class UpdateNickname(Resource):
    
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
        if validDevice_info != request_device_info:
            return {'message': 'invalid device'}, 401
        
        user = User.query.filter_by( id=validUserID ).first()
        
        if user is None:
            return {'message': 'User not Found'}, 404
        
        elif user.email != validUserEmail:
            return {'message': 'User Email in Token not match in Server'}, 400
        
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
        