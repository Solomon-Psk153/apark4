from flask_restful import Resource, reqparse
from FunctionClass import MailProvider
from DBClass import User, db
from FunctionClass import createHash
from sqlalchemy.orm.exc import NoResultFound

class SendNewPassword(Resource):
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help = 'email must be string and necessary key')
        args = parser.parse_args(strict=True)
        email=args['email']
        print(email)
        
        try:
            user = User.query.filter(User.email==email).first()
            if user is not None:
                code = MailProvider.randomCodeCreator('password')
                hashedPasswd = createHash(code, addSalt=True)
                user.passwd = hashedPasswd
                
                # https://stackoverflow.com/questions/9667138/how-to-update-sqlalchemy-row-entry
            # else:
            #     return {'message': 'User not found'}, 404
                db.session.commit()
                sender = MailProvider(dest=email,
                              subject='Recycle Mate 비밀번호 리셋',
                              code=code )        
        
                return sender.sendMail()
            
            else:
                return {'message': 'User not found'}, 404
            
        except NoResultFound as e:
            return {'message': f'User not found({e})'}, 404
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'An error occurred: {e}'}, 500
        
        finally:
            db.session.close()
    
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response