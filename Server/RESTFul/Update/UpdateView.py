from flask_restful import Resource, reqparse
from flask import request
from FlaskAPP import app
from datetime import timedelta
import jwt, redis
from DBClass import *
from FunctionClass import placeUpdate
from FunctionClass import *

class UpdateView(Resource):
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
            return {'message': 'Writing not found'}, 404
        
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        isIView = redis_client.get(validUserID)
        
        if not isIView:
            print(isIView)
            redis_client.setex(validUserID, timedelta(minutes=1), value='True')
            
            try:
                writing.views += 1
                db.session.commit()
                
                # redis를 이용해서 정보를 저장해서 1분 이후에 게시글을 방문하면 다시 증가되도록 한다.
                return {'message': 'view count increased successfully'}, 200
            
            except Exception as e:
                db.session.rollback()
                return {'message': f'internal server error: {str(e)}'}, 500
                
            finally:
                placeUpdate(user)
                db.session.close()
                
        else:
            return {'message': 'View count not increased. wait for the cooldown'}, 200