import random
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
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        # tokenCheck
        
        # 폼 데이터와 파일 데이터 추출
        title = request.form.get('title')
        contentText = request.form.get('contentText')
        type = request.form.get('type')
        whichWriting = request.form.get('whichWriting', None)
        
        try:
            image_lines = json.loads(request.form.get('image_lines', '[]'))
        except json.JSONDecodeError:
            return {'message': 'JSONDecodeError'}, 400
            
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
        folder=f'images/{type}/{createHash(author, type, title, createTime)}/'
        
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
            type=type,
            folder=folder
        )
        
        os.makedirs(os.path.dirname(folder),exist_ok=True)
        
        print('hash, author, title, contentText, createTime, modifyTime, thumbsUp, views, whichWriting, type')
        print(hash, author, title, contentText, createTime, modifyTime, thumbsUp, views, whichWriting, type)
        
        storedImages = []
        files = []
        
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        print( len(request.files) )
        
        for i, file in enumerate(request.files):
            file = request.files[file]
            print('이제 이미지 처리', i)
            print(file)
            name = file.filename
            print("name: ", name)
            path = storedWriting.folder
            whichLine = int(image_lines[i])
            imageType = file.content_type
            
            while whichLine in [newImage.whichLine for newImage in storedImages]:
                whichLine = random.randint(-2147483648, 2147483647)
                name = str(whichLine)
            
            storedImages.append(
                Image(
                    name=name,
                    whichWriting=hash,
                    whichLine=whichLine,
                    fileLocation=path,
                    imageType=imageType,
                    storeTime=createTime
                )
            )
            
            print('이미지를 리스트에 저장 단계 이후')
            print(whichLine)
            print("len:", len(storedImages))
            
            files.append(file)

        try:
            db.session.add(storedWriting)
            db.session.commit()
            
            if storedImages:
                for i, storedImage in enumerate(storedImages):
                    path = storedImage.fileLocation + storedImage.name
                    
                    print(path)

                    files[i].save(path)
                    db.session.add(storedImage)
                    
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