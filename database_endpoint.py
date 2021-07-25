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
def shutdown_session(response_or_exc):
    g.session.commit()
    g.session.remove()


"""
-------- Helper methods (feel free to add your own!) -------
"""


def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    pass


"""
---------------- Endpoints ----------------
"""


@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        print("---------haha---------")
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

        # The platform must be either “Algorand” or "Ethereum".
        # Your code should check whether “sig” is a valid signature of json.dumps(payload), 
        # using the signature algorithm specified by the platform field. 
        # Be sure to verify the payload using the sender_pk.
        sig = content['sig']
        payload = content['payload']
        pk = content['payload']['sender_pk']
        platform = content['payload']['platform']
        payload_json = json.dumps(payload)

        result = False

        if platform == "Algorand":
            print("Algorand")
            if algosdk.util.verify_bytes(payload_json.encode('utf-8'), sig, pk):
                print("Algo sig verifies!")
                pirnt("AAAAAA")
                result = True


        elif platform == "Ethereum":
            print("Ethereum")
            eth_encoded_msg = eth_account.messages.encode_defunct(text=payload_json)
            if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == pk:
                print("Eth sig verifies!")
                pirnt("EEEEE")
                result = True

        jsonify(True)

        # If the signature verifies, store the signature, 
        # as well as all of the fields under the ‘payload’ in the “Order” table EXCEPT for 'platform’.

        # If the signature does not verify, do not insert the order into the “Order” table.
        # Instead, insert a record into the “Log” table, with the message field set to be json.dumps(payload).

        # In this assignment, you will not need to match or fill the orders, 
        # simply insert them into the database (if the signature verifies).


@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session

    # The “/order_book” endpoint should return a list of all orders in the database. 
    # The response should contain a single key “data” that refers to a list of orders formatted as JSON. 
    # Each order should be a dict with (at least) the following fields 
    # ("sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", “signature”).

    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
