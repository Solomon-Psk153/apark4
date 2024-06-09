import hashlib

def stringColor(s):
    # 문자열의 해시값을 구합니다.
    hash_object = hashlib.sha256(s.encode())
    hex_dig = hash_object.hexdigest()
    
    # 해시값의 처음 6자리를 색상 코드로 사용합니다.
    color_code = '#' + hex_dig[:6]
    return color_code