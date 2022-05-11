"""
Registration of a user 0 tokens
Each user gets 10 tokens
Store a sentence on our database for 1 token
Retrieve his stored sentence on out database for 1 token
"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDatabase
users = db["Users"]

class Register(Resource):
    def post(self):
        #Step 1 is to get posted data by the user
        postedData = request.get_json()

        #Get the data
        username = postedData["username"]
        password = postedData["password"] #"123xyz"


        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        #Store username and pw into the database
        users.insert_one({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens":6
        })

        retJson = {
            "status": 200,
            "msg": "You successfully signed up for the API"
        }
        return jsonify(retJson)

def verifyPw(username, password):
    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username":username
    })[0]["Tokens"]
    return tokens

class Store(Resource):
    def post(self):
        #Step 1 get the posted data
        postedData = request.get_json()

        #Step 2 is to read the data
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        #Step 3 verify the username pw match
        correct_pw = verifyPw(username, password)

        if not correct_pw:
            retJson = {
                "status":302
            }
            return jsonify(retJson)
        #Step 4 Verify user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        #Step 5 store the sentence, take one token away  and return 200OK
        users.update_one({
            "Username":username
        }, {
            "$set":{
                "Sentence":sentence,
                "Tokens":num_tokens-1
                }
        })

        retJson = {
            "status":200,
            "msg":"Sentence saved successfully"
        }
        return jsonify(retJson)

class Get(Resource):
    def post(self):
        retJson = {
                "status": 200,
                "message": "posting"
            }
        return jsonify(retJson) 

    def get(self):
        # Step1: Get posted data by the user
        postedData = request.get_json()

        # Step2: Get the data
        username = postedData["username"]
        password = postedData["password"]

        # Step3: verify user password match
        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)
        
        # Step4: Verify user has enough tokens
        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        # Step5: get the sentence and return 200
        sentence = users.find({
            "Username":username
        })[0]["Sentence"]

        retJson = {
                "status": 200,
                "sentence": sentence
            }
        return jsonify(retJson)

api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/retrive")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0')
