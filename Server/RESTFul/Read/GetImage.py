from flask_restful import Resource, reqparse
from flask import send_from_directory
import os
# import jwt
# from DBClass import *
        
class GetImage(Resource):
    
    def post(self):
        
        # token = request.headers.get('Authorization')
        
        # if not token:
        #     return {'message': 'Token is missing, Unauthorization'}, 401
        
        # try:
        #     decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        #     validUserID = decoded['id']
        #     validUserEmail = decoded['email']
        #     validDevice_info = decoded['device_info']
        # except jwt.ExpiredSignatureError:
        #     return {'message': 'Token has expired'}, 401
        # except jwt.InvalidTokenError:
        #     return {'message': 'Invalid token'}, 401
        
        # request_device_info = request.headers.get('Device-Info')
        # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # print("device_info:", validDevice_info, "\nDevice-Info:", request_device_info)
        # if validDevice_info != request_device_info:
        #     return {'message': 'invalid device'}, 401
        
        # user = User.query.filter_by( id=validUserID ).first()
        
        # if user is None: # 토큰으로 사용자를 DB에서 찾았을 때, 존재하지 않음
        #     return {'message': 'User not Found'}, 404
        
        # elif user.email != validUserEmail:
        #     return {'message': 'User Email in Token not match in Server'}, 400
        
        parser = reqparse.RequestParser()
        parser.add_argument('directory', type=str, required=True, help='directory must be string and necessary key')
        parser.add_argument('file', type=str, required=True, help='file must be string and necessary key')
        print('before parse_args')
        args = parser.parse_args(strict=True)
        
        directory = args['directory']
        file = args['file']
        
        try:
            # Check if file exists in the directory
            if not os.path.exists(os.path.join(directory, file)):
                return {'message': 'File not found'}, 404

            # Send the file
            return send_from_directory(directory, file)

        except Exception as e:
            return {'message': f'internal server error: {str(e)}'}, 500