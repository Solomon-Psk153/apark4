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
        
            response = tokenCheck()
        
            if response[1] > 300:
                return response 
            
            validUserID = response['validUserID']
            validUserEmail = response['validUserEmail']
            validDevice_info = response['validDevice_info']
            user = response['user']
        
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