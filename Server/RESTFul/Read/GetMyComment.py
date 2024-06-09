from flask_restful import Resource
from flask import request
from DBClass import *
from FlaskAPP import app
import jwt


class GetMyComment(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        myComments = WritingSchema().dump( (Writing.query.filter( Writing.author == validUserID), Writing.type == 'commnet' ).all() )
        
        return {'message': myComments}, 200