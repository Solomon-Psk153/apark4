from FlaskAPP import app
from datetime import datetime, timedelta, timezone
import jwt

def generateToken(userID, userEmail, device_info):
    token = jwt.encode({
        'id': userID, 
        'email': userEmail,
        'device_info': device_info,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=60)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return token

# https://blog.miguelgrinberg.com/post/it-s-time-for-a-change-datetime-utcnow-is-now-deprecated