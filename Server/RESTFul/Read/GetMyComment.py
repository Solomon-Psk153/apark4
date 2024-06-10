from flask_restful import Resource
from flask import request
from DBClass import *
from FlaskAPP import app
import jwt
from FunctionClass import *


class GetMyComment(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        myComments = WritingSchema().dump( (Writing.query.filter( Writing.author == validUserID), Writing.type == 'commnet' ).all() )
        
        return {'message': myComments}, 200