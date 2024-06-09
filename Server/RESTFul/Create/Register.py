from flask import request
from flask_restful import Resource, reqparse
from DBClass import User, UserSchema
import hashlib
from DBClass import db
from FunctionClass import createHash

class Register(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, required=True, help='id must be string and necessary key')
        parser.add_argument('passwd', type=str, required=True, help='passwd must be string and necessary key')
        parser.add_argument('email', type=str, required=True, help='email must be string and necessary key')
        parser.add_argument('nickname', type=str, required=True, help='nickname must be string and necessary key')
        parser.add_argument('place', type=str, help='place must be string')
        parser.add_argument('status', type=str, help='status must be string')
        args = parser.parse_args(strict=True)
        userID = args['id']
        passwd = args['passwd']
        nickname = args['nickname']
        email = args['email']
        place = args['place'] if args['place'] else '길거리'
        status = args['status'] if args['status'] else '활성'
        
        user = User.query.filter( 
            (User.id == userID) , 
            (User.nickname == nickname) , 
            (User.email == email)
        ).first()
        
        if user is not None:
            return {'message': 'user already in app'}, 400
        
        try:
            db.session.add(
                User(
                    id=userID, 
                    passwd=createHash(passwd, addSalt=True), 
                    nickname=nickname, 
                    email=email, 
                    place=place, 
                    status=status
                )
            )
            db.session.commit()
            return {'message': 'User is created successfully'}, 201
        
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': 'Error creating user: {}'.format(e)}, 500
        
        finally:
            db.session.close()
            
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response