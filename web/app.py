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
        list_form = [
            'username',
            'password'
        ]

        dict_resp = fc.get_data_form(list_form)

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
        list_form = [
            'admin_username',
            'admin_password',
            'account',
            'amount',
        ]

        dict_resp = fc.get_data_form(list_form)

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


class Subtract(Resource):
    def post(self):
        list_form = [
            'admin_username',
            'admin_password',
            'account',
            'amount',
        ]

        dict_resp = fc.get_data_form(list_form)

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
        
        resp_json = fc.subtract_amount(dict_resp['account'], dict_resp['amount'])

        return jsonify(resp_json)


class Transfer(Resource):
    def post(self):
        list_form = [
            'username',
            'password',
            'account',
            'amount'
        ]

        dict_resp = fc.get_data_form(list_form)

        if dict_resp['status_code'] != 200:
            return dict_resp
        
        try:
            amount = float(dict_resp['amount'])
        except Exception as e:
            return jsonify(
                {
                    'message': str(e),
                    'status_code': 305,
                }
            )
        
        if amount <= 0:
            return jsonify(
                {
                    'message': "For transfer founds you need pass a number bigger than 0",
                    'status_code': 304
                }
            )

        if not fc.valid_user_and_passoword(dict_resp['username'], dict_resp['password']):
            return jsonify(
                {
                    'message': "Wrong Username or Password",
                    'status_code': 302,
                }
            )

        if not fc.valid_account(dict_resp['account']):
            return jsonify(
                {
                    'message': "The account you provide does not exist",
                    'status_code': 303,
                }
            )
        
        dict_json = fc.transfer(
            dict_resp['username'],
            dict_resp['account'],
            dict_resp['amount']
        )

        return jsonify(dict_json)


class CheckUsername(Resource):
    def post(self):
        list_form = [
            'username',
            'password',
        ]

        dict_resp = fc.get_data_form(list_form)

        if not fc.valid_user_and_passoword(dict_resp['username'], dict_resp['password']):
            return jsonify(
                {
                    'message': "Wrong Username or Password",
                    'status_code': 302,
                }
            )
        
        resp_json = fc.check_user_account(dict_resp['username'])

        return jsonify(resp_json)


class CheckAccount(Resource):
    def post(self):
        list_form = [
            'account',
            'password',
        ]

        dict_resp = fc.get_data_form(list_form)

        if not fc.valid_account_and_password(dict_resp['account'], dict_resp['password']):
            return jsonify(
                {
                    'message': "Wrong Username or Password",
                    'status_code': 302,
                }
            )
        
        resp_json = fc.check_account(dict_resp['account'])

        return jsonify(resp_json)


class DeleteAccount(Resource):
    def post(self):
        list_form = [
            'account',
            'password',
        ]

        dict_resp = fc.get_data_form(list_form)

        if not fc.valid_account_and_password(dict_resp['account'], dict_resp['password']):
            return jsonify(
                {
                    'message': "Wrong Username or Password",
                    'status_code': 302,
                }
            )
        
        resp_json = fc.delete_account(dict_resp['account'])

        return resp_json


class TransferCredit(Resource):
    def post(self):
        list_form = [
            'username',
            'password',
            'account',
            'amount'
        ]

        dict_resp = fc.get_data_form(list_form)

        if dict_resp['status_code'] != 200:
            return dict_resp
        
        try:
            amount = float(dict_resp['amount'])
        except Exception as e:
            return jsonify(
                {
                    'message': str(e),
                    'status_code': 305,
                }
            )
        
        if amount <= 0:
            return jsonify(
                {
                    'message': "For transfer credits you need pass a number bigger than 0",
                    'status_code': 304
                }
            )
        
        if not fc.valid_user_and_passoword(dict_resp['username'], dict_resp['password']):
            return jsonify(
                {
                    'message': "Wrong Username or Password",
                    'status_code': 302,
                }
            )
        
        if not fc.valid_account(dict_resp['account']):
            return jsonify(
                {
                    'message': "The account you provide does not exist",
                    'status_code': 303,
                }
            )
        
        dict_json = fc.transfer_credit(
            dict_resp['username'],
            dict_resp['account'],
            dict_resp['amount']
        )

        return dict_json


api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Transfer, "/transfer")
api.add_resource(CheckUsername, "/check-username")
api.add_resource(CheckAccount, "/check-account")
api.add_resource(DeleteAccount, "/delete-account")
api.add_resource(Subtract, "/subtract")
api.add_resource(TransferCredit, "/transfer-credit")


if __name__ == '__main__':
    initialize_debugger()

    fc.set_admin_in_db()

    app.run(
        host = app.config['HOST'],
        port = app.config['PORT'], 
        debug= app.config['DEBUG']
        )
