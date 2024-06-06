from flask_restful import Resource, reqparse
from flask import request
from FlaskAPP import app
import jwt
from DBClass import *

class UpdateLike(Resource):
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
                return {'message': 'i like this writing'}, 200
            else:
                db.session.delete(isILike)
                db.session.commit()
                return {'message': 'no interesting writing'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'internal server error: {str(e)}'}, 500
        
        finally:
            db.session.close()
            