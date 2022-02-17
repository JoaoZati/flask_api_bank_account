from app import admin, users, app
from flask import request
import bcrypt


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


def get_data_form(list_items_form: list):
    dict_resp = {
        'status_code': 200,
        'message': 'Ok'
    }

    try:
        post_data = request.get_json()

        for item in list_items_form:
            dict_resp[item] = post_data[item]

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


def valid_account_and_password(account, password):
    try:
        hash_password = str(users.find({"Account": account})[0]["Password"])
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


def transfer(username, account, amount):
    amount_username_old = users.find({"Username": username})[0]['Amount']
    amount_username = amount_username_old - amount

    if amount_username < 0:
        return {
            "messange": "You don't have enouth money in your account to transfer this amount",
            "status_code": 306,
        }

    try:
        users.update_one(
            {"Username": username},
            {
                "$set": {
                    "Amount": amount_username
                    }
            } 
        )

        amount_account_old = users.find({"Account": account})[0]['Amount']
        amount_account = amount_account_old + amount

        users.update_one(
            {"Account": account},
            {
                "$set": {
                    "Amount": amount_account
                    }
            } 
        )
    except Exception as e:
        users.update_one(
            {"Username": username},
            {
                "$set": {
                    "Amount": amount_username_old
                    }
            } 
        )

        users.update_one(
            {"Account": account},
            {
                "$set": {
                    "Amount": amount_account_old
                    }
            } 
        )

        return {
            "messange": "Some intern error have occured, you transfer was not done",
            "status_code": 305,
            }

    dict_json = {
        'message': 'Ok',
        'status_code': 200,
        'old_total_amount': amount_username_old,
        'total_transfered': amount,
        'new_total_amount': amount_username,
    }

    return dict_json


def check_user_account(username):
    user = users.find({"Username": username})[0]

    return {
        'message': 'Ok',
        'status_code': 200,
        'username': user['Username'],
        'account': user['Account'],
        'amount': user['Amount'],
        'credit': user['Credit'],
        'credit_limit': user['Credit_limit']
    }


def check_account(account):
    user = users.find({"Account": account})[0]

    return {
        'message': 'Ok',
        'status_code': 200,
        'username': user['Username'],
        'account': user['Account'],
        'amount': user['Amount'],
        'credit': user['Credit'],
        'credit_limit': user['Credit_limit']
    }


def delete_account(account):
    user = users.find({"Account": account})[0]

    amount, credit, username = user['Amount'], user['Credit'], user['Username']

    if amount or credit:
        return {
            "message": "Your account must be empty to delete",
            "status_code": 307,
            "amount": amount,
            "credit": credit
        }

    users.delete_one(
        {
            'Account': account
        }
    )

    return {
        'message': 'Your account was succesfuly deleted',
        'status_code': 200,
        'account': account,
        'username': username
    }


def subtract_amount(account, amount):
    account_amound = users.find({"Account": account})[0]['Amount']
    new_amount = account_amound - amount

    if new_amount < 0:
        return {
            "message": "This account dont have enouth fouds to take this load",
            "status_code": 308,
            "amount": amount,
            "account_amount": account_amound
        }

    users.update_one(
        {"Account": account},
        {
            "$set": {
                "Amount": new_amount
                }
        } 
    )

    return {
            "message": "Ok",
            "status_code": 200,
            "amount": amount,
            "new_amount": new_amount,
            "account_amount": account_amound
        }
