from flask_restful import Resource, reqparse
from DBClass import User

class CheckUserNickname(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True, help = 'nickname must be string and necessary key')
        args = parser.parse_args(strict=True)
        nickname = args['nickname']
        
        lenNickname = len(nickname)
        
        if User.query.filter_by(nickname=nickname).first() is not None:
            return {'message': 'nickname is alreay exist'}, 409
        
        elif lenNickname < 3:
            return {'message': 'nickname is too short'}, 400
        
        elif lenNickname > 15:
            return {'message': 'nickname is too long'}, 400
        
        else:
            return {'message': 'good nickname'}, 200
