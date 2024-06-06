import hashlib
import os

def createHash(*args, addSalt=False):
    combineString = ''.join(map(str, args))
    salt_file_path = os.path.join(os.path.dirname(__file__), 'salt')
    if addSalt:
        try:
            with open(salt_file_path, 'r') as f:
                combineString += f.read()
        except FileNotFoundError:
            return {'message': 'Salt file not found'}, 500
    
    hashObj = hashlib.sha512()
    hashObj.update(combineString.encode('utf-8'))
    hash = hashObj.hexdigest()
    
    return hash