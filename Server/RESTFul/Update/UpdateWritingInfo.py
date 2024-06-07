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
        
        data = request.form  # JSON 데이터 파싱
        hash = data.get('hash')
        title = data.get('title')
        contentText = data.get('contentText')
        
        try:
            new_image_lines = json.loads(data.get('new_image_lines', '[]'))
            remainImages = json.loads(data.get('remainImages', '[]'))
            
        except json.JSONDecodeError:
            return {'message': 'JSONDecodeError'}, 400
        
        writing = Writing.query.filter( ( Writing.hash == hash ), ( Writing.author == validUserID ) ).first()
        
        if not isinstance(new_image_lines, list):
                return {"message": "images must be a list of dictionaries and necessary key"}, 400

        print(f"hash: {hash}, title: {title}, contentText: {contentText}, images: {new_image_lines}")
        
        newImages = []
        files = []
        
        print( len(request.files) )
        for i in range(len(request.files)):
            file = request.files[f'images{i + 1}']
            name = file.filename
            type = writing.type
            path = f'images/{type}/{createHash(validUserID, type, title, writing.createTime)}/'
            whichLine = int(new_image_lines[i])
            imageType = file.content_type

            newImages.append(
                Image(
                    name=name,
                    whichWriting=hash,
                    whichLine=whichLine,
                    fileLocation=path,
                    imageType=imageType
                )
            )
            
            files.append(file)
            
        storedImages = Image.query.filter( Image.whichWriting == hash ).order_by( Image.name.asc() ).all()
        storedImagesDir = storedImages[0].fileLocation
        
        try:
            writing.title = title
            writing.contentText = contentText
            writing.modifyTime = datetime.now(timezone.utc)
            
            if storedImagesDir and os.path.exists(storedImagesDir):
                deletedImages = [storedImage.name for storedImage in storedImages]
                
                for remainImage in remainImages:
                    if remainImage['name'] in deletedImages:
                        deletedImages.remove(remainImage['name'])

                if deletedImages:
                    for deletedImage in deletedImages:
                        os.remove( os.path.abspath(storedImagesDir + deletedImage) )
                # shutil.rmtree( os.path.abspath(storedImagesDir) )
                # for storedImage in storedImages:
                #     db.session.delete(storedImage)
            
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
            return {'message': f'internal server error: {str(e)}'}, 500
        
        finally:
            placeUpdate(user)
            db.session.close()