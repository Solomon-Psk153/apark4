from datetime import timedelta
import os
from flask import Flask
from flask_restful import Api
from DBClass import *
from RESTFul import *

# curDir = os.path.abspath(os.path.dirname(__file__))
# imgDir = curDir + '/images/'

class AppConfig(object):
    DEBUG = True
    FLASK_APP = 'parkDev'
    ENV = 'development'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    # IMAGE_FORDER = COVER_IMAGE_FORDER = image_folder = imgDir
    # IMAGE_URL = 'http://127.0.0.1:5901/images/'
    
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_POOL_RECYCLE = 3600
    JSON_AS_ASCII = False
    SQLALCHEMY_DATABASE_URI = 'mysql://psk153:20183317@localhost/Ipark4'
    
app = Flask(__name__)
app.config.from_object(AppConfig)
app.secret_key='jkhfah7823JHUH&*(E@NM90wserqo)(QEOz)'

if __name__ == '__main__':

    api = Api(app)
    
    # https://stackoverflow.com/questions/19261833/what-is-an-endpoint-in-flask
    # create
    api.add_resource(Register, '/api/create/register')
    api.add_resource(CheckUserID, '/api/create/register/check/userID')
    api.add_resource(CheckUserPassword, '/api/create/register/check/password')
    api.add_resource(CheckUserNickname, '/api/create/register/check/nickname')
    api.add_resource(CheckUserEmail, '/api/create/register/check/email/format')
    api.add_resource(SendVerifyCode, '/api/create/register/check/email/send')
    api.add_resource(CheckVerifyCode, '/api/create/register/check/email/verify')
    api.add_resource(SendID, '/api/create/search/sendid')
    api.add_resource(SendNewPassword, '/api/create/search/sendpassword')
    api.add_resource(Login, '/api/create/login')
    api.add_resource(WritePost, '/api/create/users/writings')
    
    # read
    api.add_resource(GetUserProfileInfo, '/api/read/users/info')
    api.add_resource(GetWritingList, '/api/read/writing/list')
    api.add_resource(GetWritingPost, '/api/read/writing/list/post')
    api.add_resource(GetImage, '/api/read/image')
    api.add_resource(GetLike, '/api/read/writing/info/internal/like')
    api.add_resource(GetView, '/api/read/writing/info/internal/view')
    
    
    #update
    api.add_resource(UpdateNickname, '/api/update/users/info/nickname')
    api.add_resource(UpdatePasswd, '/api/update/users/info/passwd')
    api.add_resource(UpdateLike, '/api/update/writing/info/internal/like')
    api.add_resource(UpdateView, '/api/update/writing/info/internal/view')
    
    #delete
    api.add_resource(DeleteUserInfo, '/api/delete/users/info')
    
    db.init_app(app)
    app.run(host='0.0.0.0', port=5901)