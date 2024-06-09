import json
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
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        data = request.form  # JSON 데이터 파싱
        hash = data.get('hash')
        title = data.get('title')
        contentText = data.get('contentText')
        
        try:
            new_image_lines = json.loads(data.get('new_image_lines', '[]'))
            deleteImages = json.loads(data.get('deleteImageNames', '[]'))
            
        except json.JSONDecodeError:
            return {'message': 'JSONDecodeError'}, 400
        
        if not isinstance(new_image_lines, list) and isinstance(deleteImages, list):
                return {"message": "images must be a list of dictionaries and necessary key"}, 400

        print(f"hash: {hash}, title: {title}, contentText: {contentText}, images: {new_image_lines}")
        
        currentWriting = Writing.query.filter( (Writing.hash == hash),  ( Writing.author == validUserID )).first()
        
        newImages = []
        files = []
        
        print( 'len(request.files)', len(request.files) )
        
        # new file
        for i, receivedFile in enumerate(request.files):
            
            newImageName = receivedFile.filename
            newImageType = receivedFile.content_type
            
            newImages.append(
                Image(
                    name=newImageName,
                    whichWriting=hash,
                    whichLine=int(new_image_lines[i]),
                    fileLocation=f'images/{currentWriting.type}/{createHash(validUserID, currentWriting.type, currentWriting.title, currentWriting.createTime)}/',
                    imageType=newImageType
                )
            )
            
            files.append(receivedFile)
        
        storedImageObj = Image.query.filter( Image.whichWriting == hash ).first()
        storedImagesDir = None
        
        if storedImageObj:
            storedImagesDir = storedImageObj.fileLocation
        
        try:
            
            currentWriting.title = title
            currentWriting.contentText = contentText
            currentWriting.modifyTime = datetime.now(timezone.utc)
            
            db.session.commit()
            
            if deleteImages:
                for deleteImage in deleteImages:

                    deleteImageFromDB = Image.query.filter( (Image.fileLocation == deleteImage[0]), (Image.name == deleteImage[1]) ).first()
                    
                    if deleteImageFromDB:
                        db.session.delete( deleteImageFromDB )
                        os.remove( os.path.abspath(deleteImage[0] + deleteImage[1]) )
                        db.session.commit()
                
                if storedImagesDir and os.listdir(storedImagesDir) == [] and not newImages:
                    os.rmdir(storedImagesDir)
                
            if newImages:
                for i, newImage in enumerate(newImages):
                    path = newImage.fileLocation + newImage.name
                    
                    print(path)
                    
                    os.makedirs(os.path.dirname(path),exist_ok=True)
                    files[i].save(path)
                    db.session.add(newImage)
            
                db.session.commit()
            
            return {'message': 'Update writing Success'}, 200
        
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': f'internal server error: {str(e)}'}, 500
        
        finally:
            placeUpdate(user)
            db.session.close()