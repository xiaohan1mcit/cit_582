from flask import Flask, request, g
from sqlalchemy.engine.base import Transaction
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
import time
from algosdk import mnemonic

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import (
    connect_to_algo,
    connect_to_eth,
    send_tokens_algo,
    send_tokens_eth,
    wait_for_confirmation_algo,
)

from models import Base, Order, TX, Log

engine = create_engine("sqlite:///orders.db")
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
            g.icl = connect_to_algo(connection_type="indexer")
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type="indexer")

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
    msg = json.dumps(message_dict)

    # TODO: Add message to the Log table
    g.session.add(Log(logtime=datetime.now(), message=msg))
    g.session.commit()

    return


def get_algo_keys():

    # TODO: Generate or read (using the mnemonic secret)
    # the algorand public/private keys

    # mnemonic_secret = "knock ramp good scatter water step problem undo meat sketch confirm swim budget pledge impose mercy giraffe unhappy case famous swarm identify mercy able verb"
    # algo_sk = mnemonic.to_private_key(mnemonic_secret)
    # algo_pk = mnemonic.to_public_key(mnemonic_secret)

    algo_sk = "3lvsyAbs+1Vv9exQjPJdvs0Omj5OixFTe0YqtW3CaVH4GYqXqgMYuNGkPolBUj1blCF6kOGcLBcST3oaI5pKwQ=="
    algo_pk = "7AMYVF5KAMMLRUNEH2EUCUR5LOKCC6UQ4GOCYFYSJ55BUI42JLA3BUKUC4"

    return algo_sk, algo_pk


def get_eth_keys(filename="eth_mnemonic.txt"):
    # TODO: Generate or read (using the mnemonic secret)
    # the ethereum public/private keys
    # w3 = Web3()
    # mnemonic_secret = "neck stay blade method aisle coconut achieve cube message original popular ranch"
    # acct = w3.eth.account.from_mnemonic(mnemonic_secret)
    # eth_pk = acct._address
    # eth_sk = acct._private_key

    eth_pk = "0x2e42870b5374231eea72F2cE4f0862B5E95A7BcE"
    eth_sk = b'\xdd\x19\xcc\xca\t\xf5X\xa2P0\x9dM\xb6\x1c|\xd2\xca \x02\xdbc\xa6V\xb0Yr\xda]wS\xc8\xb5'

    return eth_sk, eth_pk


def fill_order(order_obj, txes=[]):
    # TODO:
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!

    # If your fill_order function is recursive, and you want to have fill_order return a list of transactions to be filled,
    # Then you can use the "txes" argument to pass the current list of txes down the recursion
    # Note: your fill_order function is *not* required to be recursive, and it is *not* required that it return a list of transactions,
    # but executing a group of transactions can be more efficient, and gets around the Ethereum nonce issue described in the instructions
    print("filling order")
    g.session.add(order_obj)
    g.session.commit()

    order_cand = match_order(order_obj)

    print("matched order #: ", order_cand, datetime.now())

    if order_cand is not None:
        derived_order, txes = process_order(order_obj, order_cand, txes)
        if derived_order is not None:
            txes.extend(fill_order(derived_order, txes))
    else:
        return txes


def match_order(order_obj):
    print("matching order")
    try:
        existing_order = g.session.query(Order).filter(Order.filled is None,
                                                       Order.buy_currency == order_obj.sell_currency,
                                                       Order.sell_currency == order_obj.buy_currency,
                                                       Order.sell_amount/Order.buy_amount >= order_obj.buy_amount/   order_obj.sell_amount)
    except Exception as e:
        print(e)
    return existing_order.first()


def process_order(order_obj, existing_order, txes):
    print("processing order")
    timestamp = datetime.now()
    order_obj.filled = timestamp
    existing_order.filled = timestamp
    order_obj.counterparty_id = existing_order.id
    existing_order.counterparty_id = order_obj.id
    g.session.commit()

    tx_order_obj_dict = {}
    tx_order_obj_dict["platform"] = order_obj.buy_currency
    tx_order_obj_dict["receiver_pk"] = order_obj.receiver_pk,
    tx_order_obj_dict["order_id"] = order_obj.id

    tx_existing_order_dict = {}
    tx_existing_order_dict["platform"] = existing_order.buy_currency
    tx_existing_order_dict["receiver_pk"] = existing_order.receiver_pk,
    tx_existing_order_dict["order_id"] = existing_order.id

    if order_obj.buy_amount < existing_order.sell_amount:  # the existing_order is partially filled
        derived_order, txes = partially_filled(order_obj, existing_order, txes)
        tx_order_obj_dict["amount"] = order_obj.buy_amount
        tx_existing_order_dict["amount"] = existing_order.buy_amount - order_obj.sell_amount
    elif order_obj.sell_amount > existing_order.buy_amount:  # the order_obj is partially filled
        derived_order, txes = partially_filled(existing_order, order_obj, txes)
        tx_order_obj_dict["amount"] = order_obj.buy_amount - existing_order.sell_amount
        tx_existing_order_dict["amount"] = existing_order.buy_amount
    else:  # exact match found
        derived_order = None
   
    txes.append(tx_order_obj_dict)
    txes.append(tx_existing_order_dict)
    
    g.session.commit()

    return derived_order, txes


def partially_filled(fullfilled_order, partiallyfilled_order, txes):
    remaining_sell_balance = partiallyfilled_order.sell_amount - fullfilled_order.buy_amount
    # exchange rate for buy/sell
    exchange_rate = partiallyfilled_order.buy_amount / partiallyfilled_order.sell_amount
    remaining_buy_balance = remaining_sell_balance * exchange_rate
    
    # generate child order of the partially filled order
    new_order = Order(sender_pk=partiallyfilled_order.sender_pk,
                      receiver_pk=partiallyfilled_order.receiver_pk,
                      buy_currency=partiallyfilled_order.buy_currency,
                      sell_currency=partiallyfilled_order.sell_currency,
                      buy_amount=remaining_buy_balance,
                      sell_amount=remaining_sell_balance,
                      filled=None,
                      creator_id=partiallyfilled_order.id,
                      counterparty_id=None)

    g.session.add(new_order)
    g.session.commit()
    return new_order, txes


def execute_txes(txes):
    print("executing order")
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print(f"Trying to execute {len(txes)} transactions")
    print(f"IDs = {[tx['order_id'] for tx in txes]}")
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()

    if not all(tx["platform"] in ["Algorand", "Ethereum"] for tx in txes):
        print("Error: execute_txes got an invalid platform!")
        print(tx["platform"] for tx in txes)

    algo_txes = [tx for tx in txes if tx["platform"] == "Algorand"]
    eth_txes = [tx for tx in txes if tx["platform"] == "Ethereum"]

    # TODO:
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table

    # for order in algo_txes:
    #     acl = connect_to_algo(connection_type="indexer")
    #     txes.append(TX(buy_currency=order.buy_currency,
    #                    sell_currency=order.sell_currency,
    #                    sender_pk=algo_pk,
    #                    receiver_pk=eth_pk,
    #                    buy_amount=order.buy_amount,
    #                    sell_amount=order.sell_amount,
    #                    tx_id=send_tokens_algo(acl, algo_sk, order)))
    #     g.session.add(order)
    #     g.session.commit()
    # for order in eth_txes:
    #     w3 = connect_to_eth()
    #     txes.append(TX(buy_currency=order.buy_currency,
    #                    sell_currency=order.sell_currency,
    #                    sender_pk=eth_pk,
    #                    receiver_pk=algo_pk,
    #                    buy_amount=order.buy_amount,
    #                    sell_amount=order.sell_amount,
    #                    tx_id=send_tokens_eth(w3, eth_sk, order)))
    #     g.session.add(order)
    #     g.session.commit()
    for tx in algo_txes:
        acl = connect_to_algo()  # (connection_type="indexer")
        print("connected to algo")
        params = acl.suggested_params()
        print("params: ", params)
        txes = TX(platform=tx.sell_currency,
                  receiver_pk=tx.receiver_pk,
                  order_id=tx.order_id,
                  tx_id=send_tokens_algo(acl, algo_sk, tx))
        print("Algo tx id", txes.tx_id)
        g.session.add(txes)
        g.session.commit()
    for tx in eth_txes:
        w3 = connect_to_eth()
        txes = TX(platform=tx.sell_currency,
                  receiver_pk=tx.receiver_pk,
                  order_id=tx.order_id,
                  tx_id=send_tokens_eth(w3, eth_sk, tx))
        print("Eth tx id", txes.tx_id)
        g.session.add(txes)
        g.session.commit()
    return True


def check_sig(payload, sig):
    sender_pk = payload['sender_pk']
    platform = payload['platform']
    payload = json.dumps(payload)
    if platform == 'Ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
        if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == sender_pk:
            return True
    elif platform == 'Algorand':
        # if algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, sender_pk):
        if algosdk.util.verify_bytes(payload.encode('utf-8'), sig, sender_pk):
            return True
    return False


""" End of Helper methods"""


@app.route("/address", methods=["POST"])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        if "platform" not in content.keys():
            print(f"Error: no platform provided")
            return jsonify("Error: no platform provided")
        if not content["platform"] in ["Ethereum", "Algorand"]:
            print(f"Error: {content['platform']} is an invalid platform")
            return jsonify(f"Error: invalid platform provided: {content['platform']}")

        if content["platform"] == "Ethereum":
            # Your code here
            eth_sk, eth_pk = get_eth_keys()
            return jsonify(eth_pk)
        if content["platform"] == "Algorand":
            # Your code here
            algo_sk, algo_pk = get_algo_keys()
            return jsonify(algo_pk)


@app.route("/trade", methods=["POST"])
def trade():
    print("In trade", file=sys.stderr)
    connect_to_blockchains()
    # get_keys()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = [
            "buy_currency",
            "sell_currency",
            "buy_amount",
            "sell_amount",
            "platform",
            "tx_id",
            "receiver_pk",
        ]
        fields = ["sig", "payload"]
        error = False
        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        error = False
        for column in columns:
            if not column in content["payload"].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        # Your code here

        # 1. Check the signature

        # 2. Add the order to the table

        # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)

        # 3b. Fill the order (as in Exchange Server II) if the order is valid

        # 4. Execute the transactions

        # If all goes well, return jsonify(True). else return jsonify(False)
        payload = content['payload']
        sig = content['sig']
        print("!!! NEW order !!!", datetime.now())
        if check_sig(payload, sig):
            print("sig checks")
            order_obj = Order(sender_pk=payload['sender_pk'],
                              receiver_pk=payload['receiver_pk'],
                              buy_currency=payload['buy_currency'],
                              sell_currency=payload['sell_currency'],
                              buy_amount=payload['buy_amount'],
                              sell_amount=payload['sell_amount'],
                              signature=sig,
                              tx_id=payload['tx_id'])

            if order_obj.sell_currency == "Algorand":
                print("Order to sell Algo")
                icl = g.icl  #connect_to_algo(connection_type="indexer")
                acl = connect_to_algo()
                print("Connecting to Algorand")
                
                txinfo = wait_for_confirmation_algo(acl, txid=order_obj.tx_id)
                time.sleep(3)
                tx = icl.search_transactions(txid=order_obj.tx_id)
                tx_value = tx["transactions"][0]["payment-transaction"]["amount"]
                tx_sender = tx["transactions"][0]["sender"]
                tx_receiver = tx["transactions"][0]["payment-transaction"]["receiver"]
                algo_sk, server_pk = get_algo_keys()
            elif order_obj.sell_currency == "Ethereum":
                print("Order to sell Eth")
                w3 = g.w3
                # print("Connecting to eth")
                tx = w3.eth.get_transaction(order_obj.tx_id)
                tx_value = tx["value"]
                tx_sender = tx["from"]
                tx_receiver = tx["to"]
                eth_sk, server_pk = get_eth_keys()
            else:
                print("false sig")
                return jsonify(False)
                
            if tx_value != order_obj.sell_amount or \
                    tx_sender != order_obj.sender_pk or \
                    tx_receiver != server_pk:
                log_message(order_obj)
                print("wrong deposit")
                return jsonify(False)

            print("ready to fill")
            txes = fill_order(order_obj)  # , txes=[])
            execute_txes(txes)
            return jsonify(True)
        else:
            print("wrong sig")
            log_message(content)
            return jsonify(False)


@app.route("/order_book")
def order_book():
    data = []
    for order in g.session.query(Order).all():
        data.append({
            'sender_pk': order.sender_pk,
            'receiver_pk': order.receiver_pk,
            'buy_currency': order.buy_currency,
            'sell_currency': order.sell_currency,
            'buy_amount': order.buy_amount,
            'sell_amount': order.sell_amount,
            'signature': order.signature,
            'tx_id': order.tx_id
        })
    return jsonify(data=data)


if __name__ == "__main__":
    app.run(port="5002")
