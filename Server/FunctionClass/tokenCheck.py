from flask import request
import jwt
from DBClass import User
from FlaskAPP import app

def tokenCheck():
    
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
    print("device_info:", validDevice_info, "\nDevice-Info:", request_device_info)
    if validDevice_info != request_device_info:
        return {'message': 'invalid device'}, 401
    
    user = User.query.filter_by( id=validUserID ).first()
    
    if user is None:
        return {'message': 'User not Found'}, 404
    
    elif user.email != validUserEmail:
        return {'message': 'User Email in Token not match in Server'}, 400
    
    return {
        'validUserID': validUserID,
        'validUserEmail': validUserEmail,
        'validDevice_info': validDevice_info,
        'user': user
        }, 0