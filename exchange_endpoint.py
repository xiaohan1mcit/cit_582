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


# check whether “sig” is a valid signature of json.dumps(payload),
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









# def fill_order(order,txes=[]):
#     pass


# the inner recursive function
def fill_order():
    # get the order you just inserted from the DB
    current_order = g.session.query(Order).order_by(Order.id.desc()).first()
    # print("_order_id")
    # print(current_order.id)

    # Check if there are any existing orders that match and add them into a list
    order_list = []
    orders = g.session.query(Order).filter(Order.filled == None).all()
    for existing_order in orders:
        # if ((existing_order.buy_amount != 0) and (current_order.sell_amount != 0)):
        if ((existing_order.buy_currency == current_order.sell_currency)
                and (existing_order.sell_currency == current_order.buy_currency)
                and (existing_order.sell_amount / existing_order.buy_amount
                     >= current_order.buy_amount / current_order.sell_amount)
                and (existing_order.counterparty_id == None)):
            order_list.append(existing_order)

    # If a match is found between order and existing_order
    if (len(order_list) > 0):
        # print(" order_list_length")
        # print(len(order_list))
        # pick the first one in the list
        match_order = order_list[0]

        # Set the filled field to be the current timestamp on both orders
        # Set counterparty_id to be the id of the other order
        match_order.filled = datetime.now()
        current_order.filled = datetime.now()
        match_order.counterparty_id = current_order.id
        current_order.counterparty_id = match_order.id
        g.session.commit()

        # if both orders can completely fill each other
        # no child order needs to be generated

        # If match_order is not completely filled
        if (current_order.sell_amount < match_order.buy_amount):
            # print("_match_order is not completely filled")
            diff = match_order.buy_amount - current_order.sell_amount
            exchange_rate_match = match_order.sell_amount / match_order.buy_amount
            sell_amount_new_match = diff * exchange_rate_match
            # print(match_order.id)
            # print(diff)
            # print(sell_amount_new_match)
            new_order = Order(sender_pk=match_order.sender_pk,
                              receiver_pk=match_order.receiver_pk,
                              buy_currency=match_order.buy_currency,
                              sell_currency=match_order.sell_currency,
                              buy_amount=diff,
                              sell_amount=sell_amount_new_match,
                              creator_id=match_order.id)
            g.session.add(new_order)
            g.session.commit()
            print("M")
            fill_order()

        # If current_order is not completely filled
        if (current_order.buy_amount > match_order.sell_amount):
            # print("_current_order is not completely filled")
            diff = current_order.buy_amount - match_order.sell_amount
            exchange_rate_current = current_order.buy_amount / current_order.sell_amount
            sell_amount_new_current = diff / exchange_rate_current
            # print(current_order.id)
            # print(diff)
            # print(sell_amount_new_current)
            new_order = Order(sender_pk=current_order.sender_pk,
                              receiver_pk=current_order.receiver_pk,
                              buy_currency=current_order.buy_currency,
                              sell_currency=current_order.sell_currency,
                              buy_amount=diff,
                              sell_amount=sell_amount_new_current,
                              creator_id=current_order.id)
            g.session.add(new_order)
            g.session.commit()
            print("C")
            fill_order()








# Takes input dictionary d and writes it to the Log table
# Hint: use json.dumps or str() to get it in a nice string form
def log_message(d):
    create_session()
    order_obj = Log(message=d)
    g.session.add(order_obj)
    shutdown_session()


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

        # TODO 1: Check the signature
        
        # extract contents from json
        sig = content['sig']
        payload = content['payload']
        platform = payload['platform']

        # The platform must be either “Algorand” or "Ethereum".
        platforms = ["Algorand", "Ethereum"]
        if not platform in platforms:
            print("input platform is not Algorand or Ethereum")
            return jsonify(False)
        
        # check signature
        check_result = check_sig(payload,sig)
        result = check_result[0]
        payload_json = check_result[1]
        
        # TODO 2: Add the order to the database
        # TODO 4: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        
        # If the signature does not verify, do not insert the order into the “Order” table.
        # Instead, insert a record into the “Log” table, with the message field set to be json.dumps(payload).
        if result is False:
            print("signature does NOT verify")
            log_message(payload_json)            
            return jsonify(result)
        
        # If the signature verifies, store the signature,
        # as well as all of the fields under the ‘payload’ in the “Order” table EXCEPT for 'platform’.
        if result is True:
            print("signature verifies")
            create_session()
            order_obj = Order(sender_pk=payload['sender_pk'],
                              receiver_pk=payload['receiver_pk'],
                              buy_currency=payload['buy_currency'],
                              sell_currency=payload['sell_currency'],
                              buy_amount=payload['buy_amount'],
                              sell_amount=payload['sell_amount'],
                              signature=sig)            
            g.session.add(order_obj)
            
            # TODO 3: Fill the order
            fill_order()
            shutdown_session()
            return jsonify(result)
        
        
        
        

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    
    # The “/order_book” endpoint should return a list of all orders in the database.
    # The response should contain a single key “data” that refers to a list of orders formatted as JSON.
    # Each order should be a dict with (at least) the following fields
    # ("sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", “signature”).
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
