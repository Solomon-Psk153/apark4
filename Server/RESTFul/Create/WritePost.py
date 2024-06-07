from flask_restful import Resource, reqparse
from flask import request
from DBClass import *
from FlaskAPP import app
from datetime import datetime, timezone
from FunctionClass import *
import os
import numpy as np
import jwt, json, hashlib

class WritePost(Resource):
    
    def post(self):
        
        token = request.headers.get('Authorization')
        
        if not token:
            return {'message': 'Token is missing, Unauthorization'}, 401
        
        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            validUserID = decoded['id']
            validUserEmail = decoded['email']
            validDevice_info = decoded['device_info']
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
        
        request_device_info = request.headers.get('Device-Info')
        if validDevice_info != request_device_info:
            return {'message': 'invalid device'}, 401
        
        user = User.query.filter_by( id=validUserID ).first()
        
        if user is None:
            return {'message': 'User not Found'}, 404
        
        elif user.email != validUserEmail:
            return {'message': 'User Email in Token not match in Server'}, 400
        
        # 폼 데이터와 파일 데이터 추출
        title = request.form.get('title')
        contentText = request.form.get('contentText')
        type = request.form.get('type')
        whichWriting = request.form.get('whichWriting', None)
        image_lines = json.loads(request.form.get('image_lines', '[]'))
        print('title, contentText, type, whichWriting, image_lines')
        print(title, contentText, type, whichWriting, image_lines)
        
        if not contentText or not type:
            return {'message': 'Missing required fields'}, 400
        
        if type not in ['post', 'comment', 'notice', 'category', 'trash']:
            return {'message': 'type out of range'}, 400
        
        elif type != 'comment' and not title:
            return {'message': "title must be member for 'post', 'notice', 'category', 'trash'"}, 400
        
        elif type in ['trash', 'comment'] and whichWriting is None:
            return {'message': 'the trash and comment must be in larger type'}, 400
        
        author = validUserID
        createTime = datetime.now(timezone.utc)
        modifyTime = None
        thumbsUp = views = 0
        hash = createHash(author, type, title, createTime, addSalt=True)
        
        # createTimeStr = createTime.strftime('%Y-%m-%d %H:%M:%S.%f')
        hash = createHash(author, type, title, createTime, addSalt = True)
        
        print('whichWriting is here', whichWriting)
        
        if whichWriting == '':
            whichWriting = None
            
        if title == None:
            title = ''
        
        storedWriting = Writing(
            hash=hash,
            author=author,
            title=title,
            contentText=contentText,
            createTime=createTime,
            modifyTime=modifyTime,
            thumbsUp=thumbsUp,
            views=views,
            whichWriting=whichWriting,
            type=type
        )
        
        print('hash, author, title, contentText, createTime, modifyTime, thumbsUp, views, whichWriting, type')
        print(hash, author, title, contentText, createTime, modifyTime, thumbsUp, views, whichWriting, type)
        
        storedImages = []
        files = []
        
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        print( len(request.files) )
        for i in range(len(request.files)): # for 문에서도 참조할 수 있나?
            print('이제 이미지 처리', i)
            file = request.files[f'images{i + 1}']
            print(file)
            name = file.filename
            print("name: ", name)
            path = f'images/{type}/{createHash(author, type, title, createTime)}/'
            whichLine = int(image_lines[i])
            imageType = file.content_type
            
            print('이미지 처리 전 단계')
            storedImages.append(
                Image(
                    name=name,
                    whichWriting=hash,
                    whichLine=whichLine,
                    fileLocation=path,
                    imageType=imageType
                )
            )
            print('이미지 처리 후 단계')
            files.append(file)
            print('이미지를 리스트에 저장 단계 이후')
            print(whichLine)
            print("len:", len(storedImages))

        try:
            db.session.add(storedWriting)
            db.session.commit()
            
            for i, storedImage in enumerate(storedImages):
                path = storedImage.fileLocation + storedImage.name
                
                print(path)
                
                os.makedirs(os.path.dirname(path),exist_ok=True)
                files[i].save(path)
                db.session.add(storedImage)
            
            if storedImages:
                db.session.commit()
            placeUpdate(user)
            
            return {'message': f'{type} {title} is written successfully'}, 201
        
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': f'server internal error: {str(e)}'}, 500
        
        finally:
            db.session.close()
    
    def after_request(self, response):
        # 응답 헤더에 Cache-Control 지시어 추가
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response