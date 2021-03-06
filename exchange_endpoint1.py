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
import math
import sys
import traceback

# self imported
from algosdk import mnemonic
import web3
from web3 import Web3, HTTPProvider

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

""" Pre-defined methods (do not need to change) """

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()

def connect_to_blockchains():
    try:
        # If g.acl has not been defined yet, then trying to query it fails
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True
    
    try:
        if acl_flag or not g.acl.status():
            # Define Algorand client for the application
            g.acl = connect_to_algo()
    except Exception as e:
        print("Trying to connect to algorand client again")
        print(traceback.format_exc())
        g.acl = connect_to_algo()
    
    try:
        icl_flag = False
        g.icl
    except AttributeError as ae:
        icl_flag = True
    
    try:
        if icl_flag or not g.icl.health():
            # Define the index client
            g.icl = connect_to_algo(connection_type='indexer')
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type='indexer')

        
    try:
        w3_flag = False
        g.w3
    except AttributeError as ae:
        w3_flag = True
    
    try:
        if w3_flag or not g.w3.isConnected():
            g.w3 = connect_to_eth()
    except Exception as e:
        print("Trying to connect to web3 again")
        print(traceback.format_exc())
        g.w3 = connect_to_eth()
        
""" End of pre-defined methods """
        
    
    
    
    
    
    
    
""" Helper Methods (skeleton code for you to implement) """

def log_message(message_dict):
    # msg = json.dumps(message_dict) # generate json string
    
    # TODO: Add message to the Log table
    create_session()
    order_obj = Log(message=message_dict)
    g.session.add(order_obj)
    shutdown_session()
    #return

    
    
    
    
    
    
    
    
    
def get_algo_keys():
    
    # TODO: Generate or read (using the mnemonic secret) 
    # the algorand public/private keys
    
    mnemonic_secret = "such chapter crane ugly uncover fun kitten duty culture giant skirt reunion pizza pill web monster upon dolphin aunt close marble dune kangaroo ability merit"
    algo_sk = mnemonic.to_private_key(mnemonic_secret)
    algo_pk = mnemonic.to_public_key(mnemonic_secret)
    
    return algo_sk, algo_pk


def get_eth_keys(filename = "eth_mnemonic.txt"):
    w3 = Web3()
    
    # TODO: Generate or read (using the mnemonic secret) 
    # the ethereum public/private keys
    
    # if mnemonic_secret == None:
    w3.eth.account.enable_unaudited_hdwallet_features()
    # acct,mnemonic_secret = w3.eth.account.create_with_mnemonic()
    # print(mnemonic_secret)
    
    mnemonic_secret = "program gym dash habit possible gate shallow exclude access report cave will"
    acct = w3.eth.account.from_mnemonic(mnemonic_secret)
    eth_pk = acct._address
    eth_sk = acct._private_key

    return eth_sk, eth_pk    
    
    
    
    
    
    
    
def fill_order(order, txes=[]):
    # TODO: 
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!
    
    pass
  
    
    
    
    
    
    
    
    
    
def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print( f"Trying to execute {len(txes)} transactions" )
    print( f"IDs = {[tx['order_id'] for tx in txes]}" )
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()
    
    if not all( tx['platform'] in ["Algorand","Ethereum"] for tx in txes ):
        print( "Error: execute_txes got an invalid platform!" )
        print( tx['platform'] for tx in txes )

    algo_txes = [tx for tx in txes if tx['platform'] == "Algorand" ]
    eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum" ]

    # TODO: 
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table

    pass








# check whether ???sig??? is a valid signature of json.dumps(payload),
# using the signature algorithm specified by the platform field.
# Be sure to verify the payload using the sender_pk.
def check_sig(payload,sig):
    
    pk = payload['sender_pk']
    platform = payload['platform']
    payload_json = json.dumps(payload)
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
    
    return result, payload_json



# convert a row in DB into a dict
def row2dict(row):
    return {
        c.name: getattr(row, c.name)
        for c in row.__table__.columns
    }



# print a dictionary nicely
def print_dict(d):
    for key, value in d.items():
        print(key, ' : ', value)



""" End of Helper methods"""












# You will need to generate a key-pair on both the Ethereum and Algorand blockchains (see more details below).
# The endpoint ???/address??? should accept a (JSON formatted) request with the argument ???platform.??? 
# The endpoint should return a (JSON formatted) response with the exchange server???s public-key on the specified platform (either ???Ethereum??? or ???Algorand???).
@app.route('/address', methods=['POST'])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        
        # check whether the input content contains a 'platform'
        if 'platform' not in content.keys():
            print( f"Error: no platform provided" )
            return jsonify( "Error: no platform provided" )
        
        # check whether the input platform is "Ethereum" or "Algorand"
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print( f"Error: {content['platform']} is an invalid platform" )
            return jsonify( f"Error: invalid platform provided: {content['platform']}"  )
        
        if content['platform'] == "Ethereum":
            #Your code here
            eth_pk = get_eth_keys()[1]
            return jsonify( eth_pk )
        
        if content['platform'] == "Algorand":
            #Your code here
            algo_pk = get_algo_keys()[1]
            return jsonify( algo_pk )

        
        
        
# should accept POST data in JSON format.
# Orders should have two fields ???payload??? and "sig".
# The payload must contain the following fields, 
# 'sender_pk???,???receiver_pk,???buy_currency???,???sell_currency???,???buy_amount???,???sell_amount???,???tx_id???,

# As in the previous assignment, the platform must be either ???Algorand??? or "Ethereum". 
# Your code should check whether ???sig??? is a valid signature of json.dumps(payload), using the signature algorithm specified by the platform field.
# If the signature verifies, the remaining fields should be stored in the ???Order??? table.
# If the signature does not verify, Instead, insert a record into the ???Log??? table, with the message field set to be json.dumps(payload).

@app.route('/trade', methods=['POST'])
def trade():
    print( "In trade", file=sys.stderr )
    connect_to_blockchains()
    get_keys()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
        fields = [ "sig", "payload" ]
        
        # Orders should have two fields ???payload??? and "sig".
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )
        
        # The payload must contain the following fields, 
        # 'sender_pk???,???receiver_pk,???buy_currency???,???sell_currency???,???buy_amount???,???sell_amount???,???tx_id???,
        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )
        
        # Your code here
        
        # 1. Check the signature
        
        # extract contents from json
        sig = content['sig']
        payload = content['payload']
        platform = payload['platform']

        # The platform must be either ???Algorand??? or "Ethereum".
        platforms = ["Algorand", "Ethereum"]
        if not platform in platforms:
            print("input platform is not Algorand or Ethereum")
            return jsonify(False)
        
        # check signature
        check_result = check_sig(payload,sig)
        result = check_result[0]
        payload_json = check_result[1]
        
        # 2. Add the order to the table
        
        # If the signature does not verify, do not insert the order into the ???Order??? table.
        # Instead, insert a record into the ???Log??? table, with the message field set to be json.dumps(payload).
        if result is False:
            print("signature does NOT verify")
            log_message(payload_json)            
            return jsonify(result)
        
        # If the signature verifies, store the signature,
        # as well as all of the fields under the ???payload??? in the ???Order??? table EXCEPT for 'platform???.
        if result is True:
            print("signature verifies")
            create_session()
            order_obj = Order(sender_pk=payload['sender_pk'],
                              receiver_pk=payload['receiver_pk'],
                              buy_currency=payload['buy_currency'],
                              sell_currency=payload['sell_currency'],
                              buy_amount=payload['buy_amount'],
                              sell_amount=payload['sell_amount'],
                              tx_id=payload['tx_id'],
                              signature=sig)            
            g.session.add(order_obj)
    
            # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)
            # In this assignment, the ???/trade??? endpoint should take an additional field ???tx_id??? which specifies the transaction ID 
            # (sometimes called the transaction hash) of the transaction that deposited tokens to the exchange. 

            # In particular, before filling an order, you must check
            # The transaction specified by tx_id is a valid transaction on the platform specified by ???sell_currency???
            # The amount of the transaction is ???sell_amount???
            # The sender of the transaction is ???sender_pk???
            # The receiver of the transaction is the exchange server (i.e., the key specified by the ???/address??? endpoint)

            # 3b. Fill the order (as in Exchange Server II) if the order is valid

            # 4. Execute the transactions

            # If all goes well, return jsonify(True). else return jsonify(False)
            return jsonify(True)

    
    
    
# should return a list of all orders in the database (the ???Order??? table). 
# The response should be a list of orders formatted as JSON. 
# Each order should be a dict with (at least) the seven key fields referenced above 
# (???sender_pk???,???receiver_pk???,???buy_currency???,???sell_currency???,???buy_amount???,???sell_amount???,???tx_id???).
@app.route('/order_book')
def order_book():
    fields = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature", "tx_id", "receiver_pk" ]
    
    # Same as before
    print("--------- order_book ---------")
    create_session()
        
    # get orders from DB into a list
    order_dict_list = [
           row2dict(order)
           for order in g.session.query(Order).all()
    ]
        
    # add the list into a dict
    result = {
        'data': order_dict_list
    }    
    
    print("order book length: ")
    print(len(order_dict_list))
    # print_dict(order_dict_list[-2])
    # print_dict(order_dict_list[-1])

    shutdown_session()
    return jsonify(result)





if __name__ == '__main__':
    app.run(port='5002')
