from flask_marshmallow import Marshmallow
from .DBSchemes import *

ma = Marshmallow()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        
class WritingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Writing
        
class ImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Image
        
class WritingLikeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WritingLike
        
class DumpsterLocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DumpsterLocation