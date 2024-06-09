from flask_restful import Resource, reqparse
from flask import request
from FlaskAPP import app
import jwt
from DBClass import *
from FunctionClass import *

class UpdateLike(Resource):
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
        
        if writing is None:
            return {'message': 'Writing not found'}, 404
        
        isILike = WritingLike.query.filter( WritingLike.userID == user.id ).first()
        
        try:
            if isILike is None:
                newLike = WritingLike(
                    userID=validUserID,
                    whichWriting=hash
                )
                
                db.session.add(newLike)
                db.session.commit()
                return {'message': 'no2yes'}, 200
            
            else:
                db.session.delete(isILike)
                db.session.commit()
                return {'message': 'yes2no'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'internal server error: {str(e)}'}, 500
        
        finally:
            placeUpdate(user)
            db.session.close()