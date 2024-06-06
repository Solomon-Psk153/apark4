from flask_restful import Resource, reqparse
from FunctionClass import MailProvider
from flask import session
import os, redis
from datetime import timedelta

class SendVerifyCode(Resource):
    # https://stackoverflow.com/questions/34762376/right-http-verb-for-sending-email
    def post(self):
        
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
        
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help = 'email must be string and necessary key')
        args = parser.parse_args(strict=True)
        email = args['email']
        
        code = MailProvider.randomCodeCreator('register')
        sender = MailProvider(
                    dest=email,
                    subject='Recycle Mate 회원가입 인증 코드',
                    code = code 
                )
        
        print(code, type(code))
        
        redis_client.setex(email, timedelta(minutes=2), value=code)
            
        return sender.sendMail()
    
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response