from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

# These decorators allow you to use g.session to access the database inside the request code
# g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals

@app.before_request
def create_session():
    g.session = scoped_session(DBSession) 

@app.teardown_appcontext
# def shutdown_session(response_or_exc):
def shutdown_session(exception=None):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """


def check_sig(payload,sig):
    pass

def fill_order(order,txes=[]):
    pass
  

# Takes input dictionary d and writes it to the Log table
# Hint: use json.dumps or str() to get it in a nice string form
def log_message(d):
    create_session()
    order_obj = Log(message=d)
    g.session.add(order_obj)
    shutdown_session()
#     pass


""" End of helper methods """


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        print("--------- trade ---------")
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        # check whether the input contains both "sig" and "payload"
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
        
        # check whether the input contains all 7 fields of payload
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )
            
        #Your code here
        #Note that you can access the database session using g.session

        # TODO: Check the signature
        
        # extract contents from json
        sig = content['sig']
        payload = content['payload']
        pk = content['payload']['sender_pk']
        platform = content['payload']['platform']
        payload_json = json.dumps(payload)

        # The platform must be either “Algorand” or "Ethereum".
        platforms = ["Algorand", "Ethereum"]
        if not platform in platforms:
            print("input platform is not Algorand or Ethereum")
            return jsonify(False)

        # check whether “sig” is a valid signature of json.dumps(payload),
        # using the signature algorithm specified by the platform field.
        # Be sure to verify the payload using the sender_pk.
        result = False

        if platform == "Algorand":
            print("Algorand")
            if algosdk.util.verify_bytes(payload_json.encode('utf-8'), sig, pk):
                print("Algo sig verifies!")
                result = True

        elif platform == "Ethereum":
            print("Ethereum")
            eth_encoded_msg = eth_account.messages.encode_defunct(text=payload_json)
            if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk:
                print("Eth sig verifies!")
                result = True
        
        # TODO: Add the order to the database
        
        # TODO: Fill the order
        
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    return jsonify(result)

if __name__ == '__main__':
    app.run(port='5002')
