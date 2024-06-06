from flask_restful import Resource, reqparse
from DBClass import User
import re
from email_validator import EmailNotValidError, validate_email

class CheckUserEmail(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        
        parser.add_argument('email', type=str, required=True, help = 'email must be string and necessary key')
        
        args = parser.parse_args(strict=True)
        email = args['email']
        
        if User.query.filter_by(email=email).first() is not None:
            return {'message': 'the email is already used'}
        
        try:
            email_regex = re.compile(r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])')
            
            if re.fullmatch(email_regex, email) == None:
                return {'message': 'email format is not good'}, 400
            
            validate_email(email) #, verify=True)
            
        except EmailNotValidError as e:
            return {'message': f'Email not valid: {str(e)}'}, 400
        
        except Exception as e:
            return {'message': f'internal server error: {str(e)}'}, 500
        
        return {'message': 'good email'}, 200
        
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response