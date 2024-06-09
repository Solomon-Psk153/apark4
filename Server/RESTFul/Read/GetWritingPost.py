from flask_restful import Resource, reqparse
from flask import request
from FunctionClass import *
from DBClass import *

class GetWritingPost(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('hash', type=str, required=True, help='hash must be string and necessary key')
        args = parser.parse_args(strict=True)
        hash = args['hash']
        
        writing = Writing.query.filter( Writing.hash == hash ).first()
        
        if writing is None:
            return {'message': 'writing not found'}, 404
        
        type = writing.type
        
        if type in ['comment', 'post']: 
        
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
        
        author = User.query.filter( User.id == writing.author ).first()
        
        if author is None:
            return {'message': 'author not found'}, 404
        
        rv = {
            'hash': writing.hash,
            'author': writing.author,
            'nickname': author.nickname,
            'place': author.place,
            'title': writing.title,
            'createTime': self.isTimeNone(writing.createTime),
            'modifyTime': self.isTimeNone(writing.modifyTime),
            'thumbsUp': writing.thumbsUp,
            'views': writing.views,
            'contentText': writing.contentText,
            'type': writing.type,
            'images': []
        }
        
        allImages = Image.query.filter( Image.whichWriting == writing.hash ).order_by( Image.name.asc() ).all()
        
        # 만약 이미지가 있다면
        if allImages:
            for image in allImages:
                rv['images'].append({
                    'name': image.name,
                    'whichLine': image.whichLine,
                    'fileLocation': image.fileLocation
                })
                
        return {'message': rv}, 200
        
    def isTimeNone(self, t):
        return t.isoformat() if t else 'None'