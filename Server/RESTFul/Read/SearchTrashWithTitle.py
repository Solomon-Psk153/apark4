from flask_restful import Resource, reqparse
from flask import request
from DBClass import *
from FunctionClass import *
from FlaskAPP import app
import jwt

class SearchTrashWithTitle(Resource):
    
    def post(self):
        
        parser = reqparse.RequestParser()
        parser.add_argument('titlePart', type=str, required=True, help='titlePart must be string and necessary key')
        
        args = parser.parse_args(strict=True)
        
        titlePart = args['titlePart']
        
        trashWritings = Writing.query.filter( (Writing.type == 'trash'), (Writing.title.like(f'%{titlePart}%')) ).all()
        
        if not trashWritings:
            return {'message': [
                {
                    'hash': '',
                    'title': '검색 결과가 없습니다.',
                    'category': '',
                    'color': '#000000'
                }
                ]}, 200 
        
        rv = []
        
        for trashWriting in trashWritings:
            category = Writing.query.filter( (Writing.type == 'category'), (Writing.hash == trashWriting.whichWriting) ).first().title
            rv.append({
                'hash': trashWriting.hash,
                'title': trashWriting.title,
                'category': category,
                'color': stringColor(category)
            })
        
        return {'message': rv}, 200