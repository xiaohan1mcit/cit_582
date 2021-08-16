from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from algosdk import mnemonic
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import math
import sys
import traceback
from web3 import Web3
from models import Base, Order, TX, Log

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth, wait_for_confirmation_algo
w3 = connect_to_eth()
acl = connect_to_algo(connection_type="indexer")
bcl = connect_to_algo(connection_type="other")

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
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True

    try:
        if acl_flag or not g.acl.status():
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


def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    # Takes input dictionary d and writes it to the Log table
    g.session.add(Log(logtime=datetime.now(), message=json.dumps(d)))
    g.session.commit()


def get_algo_keys():

    # TODO: Generate or read (using the mnemonic secret)
    # the algorand public/private keys
    algo_sk = 'aTFM7cqr8poNNLq8asdUflRYajHzrxD1A4VsB/MXia0j5kbrIg9n4PXIMw0p3v028fLYWo9UF++2YAGconKobA=='
    algo_pk = 'EPTEN2ZCB5T6B5OIGMGSTXX5G3Y7FWC2R5KBP35WMAAZZITSVBWO5JASWA'

    return algo_sk, algo_pk


def get_eth_keys(filename="eth_mnemonic.txt"):
    # TODO: Generate or read (using the mnemonic secret)
    # the ethereum public/private keys
    eth_pk = '0x539E9489881Ce6aBbf2C9Abe5Ffc017b4311E579'
    eth_sk = b'\xd71\x04\x84\x917\xf1\x85\x90\\4\xbf\xa0\xcaa\xfb\xbf\xea\xa5\xe4\x1e\x81"\x8c\xafPR\x00Z\'\xab,'

    return eth_sk, eth_pk


def fill_order(order):
    # TODO:
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!

    order_list = g.session.query(Order).filter(Order.filled == None).all()

    for matched_order in order_list:
        if matched_order.sell_currency == order.buy_currency:
            if matched_order.buy_currency == order.sell_currency:
                if ((matched_order.sell_amount / matched_order.buy_amount) >= (order.buy_amount / order.sell_amount)):

                    # Set the filled field to be the current timestamp on both orders
                    order.filled = datetime.now()
                    matched_order.filled = datetime.now()

                    # Set counterparty_id to be the id of the other order
                    order.counterparty_id = matched_order.id
                    matched_order.counterparty_id = order.id

                    txes = [order, matched_order]
                    execute_txes(txes)

                    # If one of the orders is not completely filled
                    if order.buy_amount > matched_order.sell_amount:
                        # Create a new order for remaining balance
                        remaining_balance = matched_order.buy_amount - order.sell_amount
                        ex_rate = order.buy_amount / order.sell_amount

                        derived_order_obj = Order(creator_id=order.id,
                                                  counterparty_id=None,
                                                  sender_pk=order.sender_pk,
                                                  receiver_pk=order.receiver_pk,
                                                  buy_currency=order.buy_currency,
                                                  sell_currency=order.sell_currency,
                                                  buy_amount=remaining_balance,
                                                  sell_amount=math.ceil(
                                                      remaining_balance / ex_rate),
                                                  filled=None)
                        g.session.add(derived_order_obj)
                        print("11111111")

                    elif matched_order.buy_amount > order.sell_amount:
                        # Create a new order for remaining balance
                        remaining_balance = matched_order.sell_amount - order.buy_amount
                        ex_rate = matched_order.sell_amount / matched_order.buy_amount

                        derived_order_obj = Order(creator_id=matched_order.id,
                                                  counterparty_id=None,
                                                  sender_pk=matched_order.sender_pk,
                                                  receiver_pk=matched_order.receiver_pk,
                                                  buy_currency=matched_order.buy_currency,
                                                  sell_currency=matched_order.sell_currency,
                                                  buy_amount=remaining_balance, sell_amount=math.ceil(
                                                      remaining_balance * ex_rate),
                                                  filled=None)
                        g.session.add(derived_order_obj)
                        print("222222222")
                    g.session.commit()
                    break


def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print(f"Trying to execute {len(txes)} transactions")

    algo_sk, algo_pk = get_algo_keys()
    eth_sk, eth_pk = get_eth_keys()

    if not all(tx.sell_currency in ["Algorand", "Ethereum"] for tx in txes):
        print("Error: execute_txes got an invalid platform!")
        print(tx.sell_currency for tx in txes)

    order = txes[0]
    matched_order = txes[1]
    new_txes = []

    tx1 = {
        'platform': matched_order.buy_currency,
        'receiver_pk': matched_order.receiver_pk,
        'order_id': matched_order.id,
        'tx_id': 0,
        'send_amount': 0
    }
    print("tx1: ", tx1)
    new_txes.append(tx1)
    tx2 = {
        'platform': order.buy_currency,
        'receiver_pk': order.receiver_pk,
        'order_id': order.id,
        'tx_id': 0,
        'send_amount': 0
    }
    print("tx: ", tx2)
    new_txes.append(tx2)

    if order.sell_amount < matched_order.buy_amount:

        new_txes[0]['send_amount'] = order.sell_amount
        new_txes[1]['send_amount'] = order.buy_amount

    elif matched_order.sell_amount < order.buy_amount:

        new_txes[0]['send_amount'] = matched_order.buy_amount
        new_txes[1]['send_amount'] = matched_order.sell_amount

    else:
        new_txes[0]['send_amount'] = matched_order.buy_amount
        new_txes[1]['send_amount'] = order.buy_amount

    algo_txes = [tx for tx in new_txes if tx['platform'] == "Algorand"]
    eth_txes = [tx for tx in new_txes if tx['platform'] == "Ethereum"]

    eth_TX_obj = TX(platform=eth_txes[0]['platform'],
                    receiver_pk=eth_txes[0]['receiver_pk'],
                    order_id=eth_txes[0]['order_id'],
                    tx_id=send_tokens_eth(w3, eth_sk, eth_txes))

    g.session.add(eth_TX_obj)
    g.session.commit()

    algo_TX_obj = TX(platform=algo_txes[0]['platform'],
                     receiver_pk=algo_txes[0]['receiver_pk'],
                     order_id=algo_txes[0]['order_id'],
                     tx_id=send_tokens_algo(bcl, algo_sk, algo_txes))

    g.session.add(algo_TX_obj)
    g.session.commit()


def append_order(order, data):
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


def check_sig(payload, sig):

    sender_public_key = payload['sender_pk']
    platform = payload['platform']
    payload = json.dumps(payload)
    if platform == 'Ethereum':
        eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
        if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == sender_public_key:
            return True
    elif platform == 'Algorand':
        if algosdk.util.verify_bytes(payload.encode('utf-8'), sig, sender_public_key):
            return True
    return False


def validate_tx(payload, order):

    if order.sell_currency == "Algorand":
        wait_for_confirmation_algo(connect_to_algo(), payload['tx_id'])
        algo_txes = acl.search_transactions(txid=payload['tx_id'])

        for algo_tx in algo_txes['transactions']:
            if algo_tx['payment-transaction']['amount'] == payload['sell_amount'] and algo_tx['sender'] == payload['sender_pk']:
                return True

    elif order.sell_currency == "Ethereum":
        try:
            eth_tx = w3.eth.get_transaction(payload['tx_id'])
        except Exception as e:
            print(e)
            return False
        if eth_tx['from'] == payload['sender_pk'] and eth_tx['value'] == payload['sell_amount']:
            return True

    return False


""" End of Helper methods"""


@ app.route('/address', methods=['POST'])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        if 'platform' not in content.keys():
            print(f"Error: no platform provided")
            return jsonify("Error: no platform provided")
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print(f"Error: {content['platform']} is an invalid platform")
            return jsonify(f"Error: invalid platform provided: {content['platform']}")

        if content['platform'] == "Ethereum":
            # Your code here
            eth_sk, eth_pk = get_eth_keys()
            return jsonify(eth_pk)
        if content['platform'] == "Algorand":
            # Your code here
            algo_sk, algo_pk = get_algo_keys()
            return jsonify(algo_pk)


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade", file=sys.stderr)
    connect_to_blockchains()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = ["buy_currency", "sell_currency", "buy_amount",
                   "sell_amount", "platform", "tx_id", "receiver_pk"]
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
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            return jsonify(False)

        payload = content['payload']
        sig = content['sig']
        checkSigResult = check_sig(payload, sig)
        if checkSigResult:
            order_obj = Order(sender_pk=payload['sender_pk'],
                              receiver_pk=payload['receiver_pk'],
                              buy_currency=payload['buy_currency'],
                              sell_currency=payload['sell_currency'],
                              buy_amount=payload['buy_amount'],
                              sell_amount=payload['sell_amount'],
                              signature=sig,
                              tx_id=payload['tx_id'])
            g.session.add(order_obj)
            g.session.commit()

            if validate_tx(payload, order_obj) is False:
                return jsonify(False)

            fill_order(order_obj)
            log_message(content)

        else:
            log_message(content)

        return jsonify(checkSigResult)


@ app.route('/order_book')
def order_book():
    data = []

    for order in g.session.query(Order).all():
        append_order(order, data)
    return jsonify(data=data)


if __name__ == '__main__':
    app.run(port='5002')
