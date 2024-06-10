from flask_restful import Resource, reqparse
from flask import request
from FunctionClass import *
from DBClass import *
import shutil

class DeleteWritingInfo(Resource):
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        parser = reqparse.RequestParser()
        parser.add_argument('hash', type=str, required=True, help='hash must be string and necessary key')
        args = parser.parse_args(strict=True)
        
        hash = args['hash']
        
        writing = Writing.query.filter( Writing.hash == hash ).first()

        if writing is None:
            print('Writing is None')
            return {'message': 'Writing not found'}, 404
        
        try:
            
            imageDir = Image.query.filter( Image.whichWriting == hash ).first()
            
            db.session.delete(writing)
            db.session.commit()
            
            if imageDir and os.path.exists(imageDir.fileLocation):
                shutil.rmtree( os.path.abspath(imageDir.fileLocation) )
                
            placeUpdate(user)
            return {'message': 'writing deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': f'server internal error: {str(e)}'}, 500
        
        finally:
            db.session.close()