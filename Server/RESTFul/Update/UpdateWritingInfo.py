import json
import random
from flask_restful import Resource
from flask import request
from FlaskAPP import app
import jwt
from DBClass import *
from FunctionClass import *
from datetime import datetime, timezone
import os, shutil

class UpdateWritingInfo(Resource):
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        data = request.form  # JSON 데이터 파싱
        hash = data.get('hash')
        title = data.get('title')
        contentText = data.get('contentText')
        print(title, contentText)
        try:
            new_image_lines = json.loads(data.get('new_image_lines', '[]'))
            deleteImages = json.loads(data.get('deleteImageNames', '[]'))
            
        except json.JSONDecodeError:
            return {'message': 'JSONDecodeError'}, 400
        
        if not isinstance(new_image_lines, list) and isinstance(deleteImages, list):
                return {"message": "images must be a list of dictionaries and necessary key"}, 400

        print(f"hash: {hash}, title: {title}, contentText: {contentText}, images: {new_image_lines}")
        
        currentWriting = Writing.query.filter( (Writing.hash == hash),  ( Writing.author == validUserID )).first()
        
        imagesWhichLine = [image.whichLine for image in Image.query.filter( (Image.whichWriting == currentWriting.hash) ).all()]
        
        newImages = []
        files = []
        
        print( 'len(request.files)', len(request.files) )
        
        # new file
        for i, receivedFile in enumerate(request.files):
            receivedFile = request.files[receivedFile]
            newImageName = receivedFile.filename
            newImageType = receivedFile.content_type
            
            newWhichLine = int(new_image_lines[i])
            while newWhichLine in imagesWhichLine:
                print(newWhichLine)
                newWhichLine = random.randint(0, 2147483647)
                newImageName = str(newWhichLine)
                
            while newWhichLine in [newImage.whichLine for newImage in newImages]:
                newWhichLine = random.randint(-2147483648, 2147483647)
                newImageName = str(newWhichLine)
                
            
            newImages.append(
                Image(
                    name=newImageName,
                    whichWriting=hash,
                    whichLine=newWhichLine,
                    fileLocation=currentWriting.folder,
                    imageType=newImageType,
                    storeTime=datetime.now(timezone.utc)
                )
            )
            
            files.append(receivedFile)

        try:
            
            deleteFileList = []
            saveFileList = []
            currentWriting.title = title
            currentWriting.contentText = contentText
            currentWriting.modifyTime = datetime.now(timezone.utc)
            
            print(currentWriting.title)
            print(currentWriting.contentText)
            print(currentWriting.modifyTime)
            
            db.session.commit()
            
            if deleteImages:
                for deleteImage in deleteImages:

                    deleteImageFromDB = Image.query.filter( (Image.fileLocation == deleteImage[0]), (Image.name == deleteImage[1]) ).first()
                    
                    if deleteImageFromDB:
                        db.session.delete( deleteImageFromDB )
                        # os.remove( os.path.abspath(deleteImage[0] + deleteImage[1]) )
                        deleteFileList.append( os.path.abspath(deleteImage[0] + deleteImage[1]) )
                        db.session.commit()
                
            if newImages:
                for i, newImage in enumerate(newImages):
                    path = newImage.fileLocation + newImage.name
                    
                    print('pathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpathpath',path)
                    
                    saveFileList.append(path)
                    print(newImage.whichLine)
                    print(newImage.name)
                    db.session.add(newImage)
            
                db.session.commit()
            
            
            for deleteFile in deleteFileList:
                os.remove(deleteFile)
                
            print(files, saveFileList)
            
            for i, saveFile in enumerate(saveFileList):
                files[i].save(saveFile)
            
            return {'message': 'Update writing Success'}, 200
        
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': f'internal server error: {str(e)}'}, 500
        
        finally:
            placeUpdate(user)
            db.session.close()