from flask_restful import Resource
from flask import request
from DBClass import *
from FlaskAPP import app
from FunctionClass import *
import jwt

class GetMyPost(Resource):
    
    def post(self):
        
        response = tokenCheck()
        
        if response[1] > 300:
            return response 
        
        validUserID = response[0]['validUserID']
        validUserEmail = response[0]['validUserEmail']
        validDevice_info = response[0]['validDevice_info']
        user = response[0]['user']
        
        myPosts = WritingSchema().dump( (Writing.query.filter( Writing.author == validUserID), Writing.type == 'post' ).all() )
        
        return {'message': myPosts}, 200