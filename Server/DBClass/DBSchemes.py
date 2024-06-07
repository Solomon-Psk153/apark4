from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from .DBStateShare import db

class User(db.Model):
    
    __tablename__ = 'User'
    
    id = db.Column(
        String(50), 
        nullable=False, 
        comment="사용자, 관리자의 아이디"
        )
    
    passwd = db.Column(
        String(200), 
        nullable=False, 
        comment="사용자의 비밀번호, 해쉬로 저장된다. 사용자마다 비밀번호가 같아도 고유하기 때문에 충돌 관리가 필요 없음"
        )
    
    nickname = db.Column(
        String(50), 
        nullable=False, 
        comment="사용자의 별칭"
        )
    
    email = db.Column(
        String(200), 
        nullable=False, 
        comment="사용자의 이메일"
        )
    
    place = db.Column(
        String(80), 
        nullable=False, 
        comment="사용자의 등급"
        )
    
    status = db.Column(
        String(50), 
        nullable=False, 
        comment="사용자의 상태"
        )
    
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='pk_id_user'),
        db.UniqueConstraint('nickname', name='u_nickname_user'),
        db.UniqueConstraint('email', name='u_email_user'),
        {'comment': '사람( ID, Password, 닉네임, email, 등급, 상태 )'}
    )
    
    def __init__(self, id, passwd, nickname, email, place, status):
        self.id = id
        self.passwd = passwd
        self.nickname = nickname
        self.email = email
        self.place = place
        self.status = status
    
    @classmethod
    def addUser(cls, id, passwd, nickname, email, place, status):
        try:
            db.session.add(cls(id, passwd, nickname, email, place, status))
        except:
            db.session.rollback()
            raise
        finally:
            db.session.commit()
            
    @classmethod
    def updateUserInfos(cls,id, passwd):
        
        try:
            user = cls.query.get(id)
            if user is None:
                return {"message": "user not found"}, 404
            
            setattr(user, 'passwd', passwd)
            db.session.commit()
            return {"message": "passwd has been replaced"}
        except Exception as e:
            db.session.rollback()
            return {"message": "error updating password: {}".format(str(e))}, 500

class Writing(db.Model):
    
    __tablename__ = 'Writing'
    
    hash = db.Column(
        String(200), 
        nullable=False, 
        comment="글을 구별하기 위한 고유한 값, 작성자 아이디, 생성 시간, 글의 종류, 제목으로 만든다."
        )
    
    author = db.Column(
        String(50), 
        nullable=False,
        comment="글의 작성자, user table에 id"
        )
    
    title = db.Column(
        String(150), 
        nullable=False, 
        comment="글의 이름(제목)"
        )
    
    contentText = db.Column(
        db.Text, 
        nullable=False, 
        comment="글의 내용"
        )
    
    createTime = db.Column(
        DateTime(6), 
        nullable=False, 
        comment="글이 생성된 시간"
        )
    
    modifyTime = db.Column(
        DateTime(6), 
        nullable=True, 
        comment="글이 수정된 시간"
        )
    
    thumbsUp = db.Column(
        BigInteger, 
        nullable=False, 
        default=0,
        comment="글 추천 수"
        )
    
    views = db.Column(
        BigInteger, 
        nullable=False, 
        default=0,
        comment="글 조회 수"
        )
    
    whichWriting = db.Column(
        String(200),
        nullable=True,
        comment="글이 소속되어 있는 글의 해시값"
        )
    
    type = db.Column(
        String(30), 
        nullable=False, 
        comment="게시글, 댓글, 공지사항, 카테고리, 쓰레기 중 하나의 게시글 종류"
        )

    __table_args__ = (
        db.PrimaryKeyConstraint('hash', name='pk_hash'),
        db.ForeignKeyConstraint(['whichWriting'], ['Writing.hash'], name='fk_whichWriting', ondelete='CASCADE', onupdate='CASCADE'),
        db.ForeignKeyConstraint(['author'], ['User.id'], name='fk_author', ondelete='CASCADE', onupdate='CASCADE'),
        {'comment': '글(해시값, 작성자, 글 이름, 텍스트 내용, 생성 날짜, 수정 날짜, 추천 수, 조회 수, 소속된 글의 해시값, 분류)'}
    )
    
    def __init__(self, hash, author, title, contentText, createTime, modifyTime, thumbsUp, views, whichWriting, type):
            self.hash=hash
            self.author=author
            self.title=title
            self.contentText=contentText
            self.createTime=createTime
            self.modifyTime=modifyTime
            self.thumbsUp=thumbsUp
            self.views=views
            self.whichWriting=whichWriting
            self.type=type
            
class Image(db.Model):
    
    __tablename__ = 'Image'
    
    whichWriting = db.Column(
        String(200), 
        nullable=False, 
        comment="이미지가 들어있는 글의 해시값"
        )
    
    whichLine = db.Column(
        Integer, 
        nullable=False, 
        comment="글에서 이미지의 위치"
        )
    
    fileLocation = db.Column(
        String(200), 
        nullable=False, 
        comment="이미지의 경로"
        )
    
    name = db.Column(
        String(50), 
        nullable=False, 
        comment="이미지 이름"
        )
    
    imageType = db.Column(
        String(50),
        nullable=False,
        comment="이미지 content-type"
    )

    __table_args__ = (
        db.PrimaryKeyConstraint('whichWriting', 'whichLine', 'fileLocation', name='pk_image_point_Line_Location'),
        db.ForeignKeyConstraint(['whichWriting'], ['Writing.hash'], name='fk_image_whichWriting', ondelete='CASCADE', onupdate='CASCADE'),
        {'comment': "이미지(이미지가 들어있는 글의 해시값, 글에서 이미지의 위치, 이미지의 경로)"}
    )
    
    def __init__(self, whichWriting, whichLine, fileLocation, name, imageType):
        self.whichWriting=whichWriting
        self.whichLine=whichLine
        self.fileLocation=fileLocation
        self.name=name
        self.imageType=imageType
        
class WritingLike(db.Model):
    
    __tablename__ = 'WritingLike'
    
    whichWriting = db.Column(
        String(200),
        nullable=False,
        comment="좋아요를 누른 글의 해시값"
    )
    
    userID = db.Column(
        String(50),
        nullable=False,
        comment="좋아요를 누른 사용자"
    )
    
    __table_args__ = (
        db.PrimaryKeyConstraint('whichWriting', 'userID',name='pk_userID_whichWriting'),
        db.ForeignKeyConstraint(['whichWriting'], ['Writing.hash'], name='fk_like_whichWriting', ondelete='CASCADE', onupdate='CASCADE'),
        db.ForeignKeyConstraint(['userID'], ['User.id'], name='fk_userID', ondelete='CASCADE', onupdate='CASCADE'),
        {'comment': "추천(글 해시값, 추천한 사람)"}
    )
    
    def __init__(self, whichWriting, userID):
        self.whichWriting=whichWriting
        self.userID=userID