from flask_restful import Resource, reqparse
import re

class CheckUserPassword(Resource):
    
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('passwd', type=str, required=True, help = 'passwd must be string and necessary key')
        args = parser.parse_args(strict=True)
        passwd = args['passwd']
        lenPasswd = len(passwd)
        
        if not re.match('(?=.*[!@#$%^&*()])(?=.*[0-9])(?=.*[a-zA-Z]).{8,}$', passwd):
            return {'message': 'password pattern is not good'}, 400
        
        elif lenPasswd < 8:
            return {'message': 'password len is too short'}, 400
        
        elif lenPasswd > 30:
            return {'message': 'password len is too long'}, 400
        
        else:
            return {'message': 'good password'}, 200
    
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
        
    