from flask_restful import Resource, reqparse
import re
from DBClass import User

class CheckUserID(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help = 'id must be string and necessary key')
        args = parser.parse_args(strict=True)
        userID = args['id']
        
        lenUserID = len(userID)
        
        if not re.match('^[a-zA-Z][a-zA-Z0-9]{4,}', userID):
            return {'message': 'userID pattern is not good'}, 400
        
        elif lenUserID < 5:
            return {'message': 'userID length is too short'}, 400
        
        elif lenUserID > 20:
            return {'message': 'userID length is too long'}, 400
        
        elif User.query.filter_by(id=userID).first() is not None:
            return {'message': 'userID is already exist'}, 409
        
        else:
            return {'message': 'good userID'}, 200
        
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response