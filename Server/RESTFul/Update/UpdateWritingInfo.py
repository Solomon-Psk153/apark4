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
            
        except json.JSONDecodeError:
            return {'message': 'JSONDecodeError'}, 400
        
        if not isinstance(new_image_lines, list):
                return {"message": "images must be a list of dictionaries and necessary key"}, 400

        print(f"hash: {hash}, title: {title}, contentText: {contentText}, images: {new_image_lines}")
        
        
        originalImageObjs = ImageSchema().dump( Image.query.filter( Image.whichWriting == hash ).all() )
        
        originalImageName = [originalImageObj['name'] for originalImageObj in originalImageObjs]
        originalImageIndex = [splitNameExt(name)[0][-1] for name in originalImageName]
        
        currentWriting = Writing.query.filter( (Writing.hash == hash),  ( Writing.author == validUserID )).first()
        
        newImages = []
        files = []
        
        delImages = []
        
        print( 'len(request.files)', len(request.files) )
        
        # new file
        for i, receivedFile in enumerate(request.files):
            
            newFileName = receivedFile.filename
            newImageType = receivedFile.content_type
            
            newImageName, _ = splitNameExt(newFileName)
            
            for j in range(originalImageIndex):
                if newImageName[-1] == originalImageIndex[j]:
                    delImages.append(originalImageName)
            
            
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
            
            if storedImagesDir and os.path.exists(storedImagesDir):
                if delImages:
                    for delImage in delImages:
                        
                        os.remove( os.path.abspath(delImage.path + delImage.name) )
                        db.session.delete(delImage)
                        
                    db.session.commit()
                if os.listdir(storedImagesDir) == []:
                    os.rmdir(storedImagesDir)
                
            if newImages:
                for i, newImage in enumerate(newImages):
                    path = newImage.fileLocation + newImage.name
                    
                    print(path)
                    
                    os.makedirs(os.path.dirname(path),exist_ok=True)
                    files[i].save(path)
                    db.session.add(newImage)
            
            db.session.commit()
                        
                        
            
            # if storedImagesDir and os.path.exists(storedImagesDir):
            #     deletedImages = [storedImage for storedImage in storedImages]
                
            #     for remainImage in remainImages:
            #         for deletedImage in deletedImages:
            #             if remainImage['name'] == deletedImage.name:
            #                 deletedImages.remove(deletedImage)

            #     if deletedImages:
            #         for deletedImage in deletedImages:
            #             os.remove( os.path.abspath(storedImagesDir + deletedImage) )
            #             db.session.delete(deletedImage)
            #     # shutil.rmtree( os.path.abspath(storedImagesDir) )
            #     # for storedImage in storedImages:
            #     #     db.session.delete(storedImage)
            
            return {'message': 'Update writing Success'}, 200
        
        except Exception as e:
            db.session.rollback()
            print(e)
            return {'message': f'internal server error: {str(e)}'}, 500
        
        finally:
            placeUpdate(user)
            db.session.close()