from flask_restful import Resource, reqparse
from flask import request, Response
from DBClass import *
from FlaskAPP import app
from FunctionClass import *
import jwt, json, hashlib
from requests_toolbelt.multipart.encoder import MultipartEncoder

class GetWritingPostForUpdate(Resource):
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
        
        parser = reqparse.RequestParser()
        parser.add_argument('hash', type=str, required=True, help='hash must be string and necessary key')
        
        args = parser.parse_args(strict=True)
        
        hash = args['hash']
        
        writing = Writing.query.filter( Writing.hash == hash ).first()
        
        images = Image.query.filter( Image.whichWriting == hash).order_by( Image.name.desc() ).all()
        
        image_lines = image_lines = [str(image.whichLine) for image in images]
        
        rv = {
            'title': writing.title,
            'contentText': writing.contentText,
            'image_lines': json.dumps(image_lines)
        }
                
        if images:
            for i, image in enumerate(images):
                with open(image.fileLocation + image.name, 'rb') as f:
                    rv[f'images{i}'] = (image.name, f.read(), image.imageType)
        
        multipart_data = MultipartEncoder(fields=rv)
        
        response = Response(multipart_data.to_string(), content_type=multipart_data.content_type)
        
        return response, 200
        