from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, select, MetaData, Table
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only

from models import Base, Order, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# database_endpoint.py

app = Flask(__name__)


# These decorators allow you to use g.session to access the database inside the request code
@app.before_request
def create_session():
    g.session = scoped_session(
        DBSession)  # g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals


@app.teardown_appcontext
# def shutdown_session(response_or_exc):
def shutdown_session(exception=None):
    g.session.commit()
    g.session.remove()


"""
-------- Helper methods (feel free to add your own!) -------
"""

# Takes input dictionary d and writes it to the Log table
# actually should be the JSON of the dict, not the dict
# original requirement was wrong
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
    


"""
---------------- Endpoints ----------------
"""


@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        print("--------- trade ---------")
        content = request.get_json(silent=True)
        print(f"content = {json.dumps(content)}")
        columns = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform"]
        fields = ["sig", "payload"]

        # check whether the input contains both "sig" and "payload"
        error = False
        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        # check whether the input contains all 7 fields of payload
        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            log_message(content)
            return jsonify(False)

        # Your code here
        # Note that you can access the database session using g.session

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
        
        # In this assignment, you will not need to match or fill the orders,
        # simply insert them into the database (if the signature verifies).

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
            shutdown_session()
            return jsonify(result)

        # If the signature does not verify, do not insert the order into the “Order” table.
        # Instead, insert a record into the “Log” table, with the message field set to be json.dumps(payload).
        if result is False:
            print("signature does NOT verify")
            log_message(payload_json)            
            return jsonify(result)

        
@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session

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
    print(order_dict_list[-2])
    print(order_dict_list[-1])

    shutdown_session()
    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
