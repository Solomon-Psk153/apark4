from flask_restful import Resource, reqparse
from FunctionClass import MailProvider
from DBClass import UserSchema, User

class SendID(Resource):
    # https://stackoverflow.com/questions/34762376/right-http-verb-for-sending-email
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help = 'email must be string and necessary key')
        args = parser.parse_args(strict=True)
        email=args['email']
        
        print("email:", email)
        
        user = User.query.filter(User.email==email).first()
        
        if user is None:
            return {'message': 'email not found'}, 404
        
        findID = user.id
        
        print(findID)
        
        sender = MailProvider(dest=email,
                              subject='Recycle Mate ID 찾기',
                              code=findID )
        
        return sender.sendMail()
    
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response