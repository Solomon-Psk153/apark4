from flask_restful import Resource, reqparse
from flask import send_from_directory
import os
# import jwt
# from DBClass import *
        
class GetImage(Resource):
    
    def post(self):
        
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