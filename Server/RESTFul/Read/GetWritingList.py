# import uuid
from flask_restful import Resource, reqparse
from flask import request
from sqlalchemy import func ####
from DBClass import *
from FlaskAPP import app
from FunctionClass import *
import jwt

class GetWritingList(Resource):
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
        print("device_info:", validDevice_info, "\nDevice-Info:", request_device_info)
        if validDevice_info != request_device_info:
            return {'message': 'invalid device'}, 401
        
        user = User.query.filter_by( id=validUserID ).first()
        
        if user is None: # 토큰으로 사용자를 DB에서 찾았을 때, 존재하지 않음
            return {'message': 'User not Found'}, 404
        
        elif user.email != validUserEmail:
            return {'message': 'User Email in Token not match in Server'}, 400
        
        
        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=True, help='type must be string and necessary key')
        parser.add_argument('whichWriting', type=str, required=False, help='whichWriting must be string and necessary key')
        parser.add_argument('page', type=str, required=False, help='page must be string and necessary key')
        parser.add_argument('items', type=str, required=False, help='items must be string and necessary key')
        
        args = parser.parse_args(strict=True)
        
        type = args['type']
        whichWriting = args['whichWriting']
        page = int(args['page'])
        items = int(args['items'])
        
        if whichWriting == '':
            whichWriting = None
        
        if type in ['post', 'notice', 'trash', 'category']:
            return {'message': self.getListedDict(whichWriting, page, items)}, 200
        
        elif type == 'comment':
            return {'message': self.getListedComment(whichWriting)}, 200
        
        else:
            return {'message': 'type is out of range!'}, 400
        
    def getListedComment(self, point):
        
        rv = []
        
        # comment를 시간별로 내림차순으로 정렬하고 type이 comment이고 whichWriting이 point(여기서는 어떤 글의 해시값)를 가리키는 comment를 전부 조회한다.
        allComment = Writing.query.filter( Writing.whichWriting == point, Writing.type == 'comment' ).order_by(Writing.createTime.desc()).all()
        
        # comment가 비어있으면 그냥 빈 리스트를 반환한다.        
        if not allComment:
            return rv
        
        # comment가 있다면
        for comment in allComment:
            user = User.query.filter_by( id=comment.author ).first()
            # comment가 가져야 할 데이터 목록
            commentDict = {
                    'hash': comment.hash,
                    'author':comment.author,
                    'nickname': user.nickname,
                    'place': user.place,
                    'title': comment.title,
                    'createTime': self.isTimeNone(comment.createTime),
                    'modifyTime': self.isTimeNone(comment.modifyTime),
                    'thumbsUp': comment.thumbsUp,
                    'contentText': comment.contentText,
                    'type': comment.type,
                    'images': [],
                    'childComment': []
                }
            
            # 개별 comment가 가지고 있는 모든 이미지를 조회
            allImages = Image.query.filter( Image.whichWriting == comment.hash ).all()
            
            # 만약 이미지가 있다면
            if allImages:
                for image in allImages:
                    
                    commentDict['images'].append({
                        'name': image.name,
                        'whichLine': image.whichLine,
                        'fileLocation': image.fileLocation
                    })
                    
            # 하위 댓글이 있는지 데이터베이스에서 모두 검색한다.
            childComments = Writing.query.filter( Writing.whichWriting == comment.hash).all()
            
            # 만약 하위 댓글이 또 존재하면
            if childComments:
                for childComment in childComments:
                    
                    # 하위 댓글을 또 재귀로 돌려서 모든 댓글 리스트를 얻어낸다.
                    
                    childDictList = self.getListedComment(childComment.whichWriting)
                    
                    commentDict['childComment'].extend(childDictList)
                    
                    # 하위 댓글 리스트가 존재하면 댓글 딕셔너리를 추가한다.
                    # if childDictList:
                    #     commentDict['childComment'].extend(childDictList)
            
            rv.append(commentDict)
            
        return rv
            
        
    def getListedDict(self, point=None, page=1, items_per_page=10):
        
        rv = []
        offset = (page - 1) * items_per_page
        
        # 카테고리, 공지사항, 게시글 리스트
        if point is None:
            
            # 시간 순서대로 페이지에 있는 개수를 모두 쿼리한다.
            paged_writings = Writing.query.order_by(Writing.createTime.desc())\
            .limit(items_per_page)\
            .offset(offset)\
            .all()
        
        # 쓰레기 리스트
        else:
            paged_writings = Writing.query.filter( Writing.whichWriting == point ).order_by(Writing.createTime.desc())\
            .limit(items_per_page)\
            .offset(offset)\
            .all()
        
        # 쿼리한 해시값을 리스트로 모두 구한다.
        writing_hashes = [ writing.hash for writing in paged_writings ]
        
        # Alias for the Image table
        # ImageAlias = aliased(Image)

        # Subquery to find the minimum whichLine for each whichWriting
        subquery = db.session.query(
            Image.whichWriting,
            func.min(Image.whichLine).label('min_line')
        ).filter(
            Image.whichWriting.in_(writing_hashes)
        ).group_by(
            Image.whichWriting
        ).subquery()

        # Main query to join Writing and Image with the subquery to find the first image for each writing
        writing_images = db.session.query(
            Writing,
            Image
        ).outerjoin(
            subquery,
            Writing.hash == subquery.c.whichWriting
        ).outerjoin(
            Image,
            (Writing.hash == Image.whichWriting) & (Image.whichLine == subquery.c.min_line)
        ).filter(
            Writing.hash.in_(writing_hashes)
        ).order_by(
            Writing.createTime.desc()
        ).all()
        
        for writing, image in writing_images:
            
            user = User.query.filter_by( id=writing.author ).first()
            
            rv.append({
                'hash': writing.hash,
                'author': writing.author,
                'nickname': user.nickname,
                'place': user.place,
                'title': writing.title,
                'createTime': self.isTimeNone(writing.createTime),
                'modifyTime': self.isTimeNone(writing.modifyTime),
                'thumbsUp': writing.thumbsUp,
                'views': writing.views,
                'type': writing.type,
                'thumbnailLoc': image.fileLocation if image else None,
                'thumbnailName': image.name if image else None
            })
            
            print(rv)
            
        return rv
    
    def isTimeNone(self, t):
        return t.isoformat() if t else 'None'