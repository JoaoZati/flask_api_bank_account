from app import admin, users, app
from flask import request
import bcrypt

from random import randint


def set_admin_in_db():
    try:
        admin_username = app.config['ADMIN_USERNAME']
        admin.find({"Admin": admin_username})[0]['Admin']
    except Exception as e:
        admin.delete_many({})
        hashed_password = bcrypt.hashpw(app.config['ADMIN_PASSWORD'], bcrypt.gensalt())
        admin.insert_one(
            {
                "Admin": app.config['ADMIN_USERNAME'],
                "Password": hashed_password
            }
        )
        print('Set Admin sucessfully!')


def get_data_register():
    dict_resp = {
        'status_code': 200,
        'message': 'Ok'
    }

    try:
        post_data = request.get_json()

        dict_resp['username'] = post_data["username"]
        dict_resp['password'] = post_data["password"]

    except Exception as e:
        dict_resp = {
        'status_code': 305,
        'message': str(e)
        }

    return dict_resp


def get_data_admin(add=False):
    dict_resp = {
        'status_code': 200,
        'message': 'Ok'
    }

    try:
        post_data = request.get_json()

        dict_resp['admin_username'] = str(post_data["admin_username"])
        dict_resp['admin_password'] = str(post_data["admin_password"])
    except Exception as e:
        dict_resp = {
            'status_code': 305,
            'message': str(e)
            }
    
    if add and dict_resp['status_code'] == 200:
        try:
            dict_resp['account'] = str(post_data["account"])
            dict_resp['amount'] = float(post_data["amount"])
        except Exception as e:
            dict_resp = {
                'status_code': 305,
                'message': str(e)
                }
    
    return dict_resp


def user_already_exist(username):
    try:
        if users.find({"Username": username})[0]['Username'] == username:
            return True
    except Exception as e:
        print(e)
    
    return False


def valid_user_and_passoword(username, password):
    try:
        hash_password = str(users.find({"Username": username})[0]["Password"])
        if bcrypt.hashpw(password, hash_password) == hash_password:
            return True
    except Exception as e:
        print(e)
    
    return False


def valid_admin_and_passoword(username, password):
    try:
        hash_password = str(admin.find({"Admin": username})[0]["Password"])
        if bcrypt.hashpw(password, hash_password) == hash_password:
            return True
    except Exception as e:
        print(e)
    
    return False


def get_tokens(username):
    try:
        tokens = int(users.find({"Username": username})[0]["Tokens"])
    except Exception as e:
        print(e)
        tokens = 0
    
    return tokens


def set_username_tokens(username, tokens):

    users.update_one(
        {"Username": username},
        {
            "$set": {
                "Tokens": tokens
                }
        } 
    )


def create_new_account():
    u = users.find({})
    lst_users = [x for x in u]

    last_number = 1
    if len(lst_users) != 0:
        last_number = int(lst_users[-1]['Account']) + 1

    account = [x for x in str(last_number)]
    while True:
        if len(account) >= 9:
            break
        account.append(str(0))

    return ''.join(account[::-1])


def create_new_user(username, password, dict_resp):

    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    account = create_new_account()

    dict_user = {
            "Username": username,
            "Password": hashed_password,
            "Amount": 0,
            "Credit": 0,
            "Account": account,
            "Credit_limit": 2000
        }

    users.insert_one(
        dict_user
    )

    for word in ['Amount', 'Credit', 'Account', 'Credit_limit']:
        dict_resp[word.lower()] = dict_user[word]


def valid_account(account):
    try:
        users.find({"Account": account})[0]
        return True
    except Exception as e:
        return False


def add_founds(account, amount):
    amount = users.find({"Account": account})[0]['Amount'] + amount

    users.update_one(
        {"Account": account},
        {
            "$set": {
                "Amount": amount
                }
        } 
    )
