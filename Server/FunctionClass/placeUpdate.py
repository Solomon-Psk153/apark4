from DBClass import *

def placeUpdate(user):
    
    writingCount = 0
    writingLikeCount = 0
    writings = Writing.query.filter( Writing.author == user.id ).all()
    
    if writings:
        for writing in writings:
            writingCount += 1
            writingLikeCount += writing.thumbsUp
    
    rv = writingCount + writingLikeCount / 10
    place = '길거리'
    
    if rv == 0 and rv < 30:
        pass
    
    elif rv < 100:
        place = '휴지통'
    
    elif rv < 150:
        place = '청소기'
    
    elif rv < 200:
        place = '환경미화원'
    
    elif rv < 300:
        place = '청소차'
    
    elif rv < 450:
        place = '폐기물 처리 공장'
    
    else: 
        place = '분리신'
    
    try:
        user.place = place
        db.session.commit()
        return {'message': 'place has been replaced'}, 200
    
    except Exception as e:
        db.session.rollback()
        return {'message': f'server internal error: {str(e)}'}, 500
        
    finally:
        db.session.close()