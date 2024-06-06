from flask_restful import Resource, reqparse
from FunctionClass import MailProvider
from flask import session
import os, redis

class CheckVerifyCode(Resource):
    
    def post(self):
        
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        
        parser = reqparse.RequestParser()
        parser.add_argument('code', type=str, required=True, help='code must be string and necessary key')
        parser.add_argument('email', type=str, required=True, help='code must be string and necessary key')
        args = parser.parse_args(strict=True)
        code = args['code']
        email = args['email']
        
        stored_verify_code = redis_client.get(email)
        
        if stored_verify_code:
            if stored_verify_code == code:
                redis_client.delete(email)
                return {'message': 'code match'}, 200
            
            else:
                return {'message': 'code not match'}, 400
        else:
            return {'message': 'Email code time expired'}, 400
        
    def after_request(self, response):
    # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response