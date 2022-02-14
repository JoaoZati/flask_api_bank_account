"""
Registration of a User
Each user get 10 tokens 
Sotore a sentece for 1 token
Retrive his stored sentence on our database for 1 token
"""

from re import A
from flask import Flask, jsonify
from flask_restful import Api, Resource

from pymongo import MongoClient
from debugger import initialize_debugger

import bcrypt

import facade as fc

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
api = Api(app)

client = MongoClient(app.config['DATABASE'])  # same name in docker compose
db = client.SentenceDatabase
users = db["Users"]
admin = db["Admin"]


@app.route('/')
def hello_word():
    return 'Hello Word'


class Register(Resource):
    def post(self):
        dict_resp = fc.get_data_register()

        if dict_resp['status_code'] != 200:
            return dict_resp
        
        username = dict_resp['username']
        password = dict_resp['password']
        
        if fc.user_already_exist(username):
            return jsonify(
                {
                    'Status Code': 301,
                    'Message': "User already exists",
                }
            )

        try:
            fc.create_new_user(username, password, dict_resp)
        except:
            return jsonify(
                {
                    'Status Code': 305,
                    'Message': "One internal error has occurred",
                }
            )

        return jsonify(dict_resp)


class Add(Resource):
    def post(self):
        dict_resp = fc.get_data_admin(add=True)

        if dict_resp['status_code'] != 200:
            return dict_resp

        if not fc.valid_admin_and_passoword(dict_resp['admin_username'], dict_resp['admin_password']):
            return jsonify(
                {
                    'Status Code': 303,
                    'Message': 'Invalid admin username or admin password',
                }
            )
        
        if not fc.valid_account(dict_resp['account']):
            return jsonify(
                {
                    'Status Code': 302,
                    'Message': 'Invalid account',
                }
            )
        
        try:
            fc.add_founds(dict_resp['account'], dict_resp['amount'])
        except Exception as e:
            print(e)
            return jsonify(
                {
                    'Status Code': 305,
                    'Message': "Sorry one internal error have ocurred",
                }
            )

        return jsonify(dict_resp)


class Refil(Resource):
    def post(self):
        dict_result = fc.get_data_admin()

        if dict_result['status_code'] != 200:
            return jsonify(dict_result)
        
        username = dict_result['username']
        admin_username = dict_result['admin_username']
        admin_password = dict_result['admin_password']
        refil_tokens = dict_result['refil_tokens']

        if not fc.user_already_exist(username):
            return jsonify(
                {
                    'Status Code': 302,
                    'Message': 'Invalid username',
                }
            )

        if not fc.valid_admin_and_passoword(admin_username, admin_password):
            return jsonify(
                {
                    'Status Code': 303,
                    'Message': 'Invalid admin username or admin password',
                }
            )

        tokens = fc.get_tokens(username)
        new_tokens = tokens + refil_tokens
        fc.set_username_tokens(username, new_tokens)

        dict_result['old_tokens'] = tokens
        dict_result['new_tokens'] = new_tokens

        return jsonify(dict_result)


api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Refil, "/refil")

if __name__ == '__main__':
    initialize_debugger()

    fc.set_admin_in_db()

    app.run(
        host = app.config['HOST'],
        port = app.config['PORT'], 
        debug= app.config['DEBUG']
        )
