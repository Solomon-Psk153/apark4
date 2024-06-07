import json
from flask_restful import Resource, reqparse
from flask import request
from FlaskAPP import app
import jwt
from DBClass import *
from datetime import datetime, timezone

class UpdateWritingInfo(Resource):
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
        
        data = request.get_json()  # JSON 데이터 파싱
        hash = data.get('hash')
        title = data.get('title')
        contentText = data.get('contentText')
        
        try:
            images = json.loads(data.get('images', []))
        except json.JSONDecodeError:
            return {'message': 'JSONDecodeError'}, 400
        
        writing = Writing.query.filter( (Writing.hash == hash), (Writing.author == validUserID) ).first()
        
        if not isinstance(images, list):
                return {"message": "images must be a list of dictionaries and necessary key"}, 400

        print(f"hash: {hash}, title: {title}, contentText: {contentText}, images: {images}")
        
        updateRv = {
            'title': title,
            'contentText': contentText,
            'images': []
        }
        
        if images:
            for image in images:
                updateRv.append(
                    {
                        'name': image.name,
                        'whichLine': image.whichLine,
                        'fileLocation': image.fileLocation
                    }
                )
                
        
        updateRv['modifyTime'] = datetime.now(timezone.utc)
        
        try:
            writing.title = updateRv['title']
            writing.contentText = updateRv['contentText']
            writing.images = updateRv['images']
            writing.modifyTime = updateRv['modifyTime']
            db.session.commit()
            
            return {'message': 'Update writing Success'}, 200
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'internal server error: {str(e)}'}, 500
        
        finally:
            db.session.close()