from flask_restful import Resource, reqparse
from flask import request, Response
from DBClass import *
from FlaskAPP import app
from FunctionClass import *
import jwt, json, hashlib

class GetWritingPostForUpdate(Resource):
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        parser = reqparse.RequestParser()
        parser.add_argument('hash', type=str, required=True, help='hash must be string and necessary key')
        
        args = parser.parse_args(strict=True)
        
        hash = args['hash']
        
        writing = Writing.query.filter( Writing.hash == hash ).first()
        
        images = Image.query.filter( Image.whichWriting == hash).order_by( Image.name.desc() ).all()
        
        rv = {
            'title': writing.title,
            'contentText': writing.contentText,
            'images': []
        }
        
        for image in images:
            rv['images'].append(
                {
                    'name': image.name,
                    'whichLine': image.whichLine,
                    'fileLocation': image.fileLocation,
                    'imageType': image.imageType
                }
            )
        
        return {'message': rv}, 200