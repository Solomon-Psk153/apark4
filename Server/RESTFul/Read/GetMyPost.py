from flask_restful import Resource
from flask import request
from DBClass import *
from FlaskAPP import app
import jwt

class GetMyPost(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response['validUserID']
        validUserEmail = response['validUserEmail']
        validDevice_info = response['validDevice_info']
        user = response['user']
        
        myPosts = WritingSchema().dump( (Writing.query.filter( Writing.author == validUserID), Writing.type == 'post' ).all() )
        
        return {'message': myPosts}, 200