#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk.v2client import indexer
from algosdk import account
from algosdk.future import transaction

def connect_to_algo(connection_type=''):
    #Connect to Algorand node maintained by PureStake
    algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
    headers = {'X-Api-key': algod_token}
#     purestake_token = {'X-Api-key': algod_token}
    
    if connection_type == "indexer":
        # TODO: return an instance of the v2client indexer. This is used for checking payments for tx_id's
        algod_address = "https://testnet-algorand.api.purestake.io/idx2"
#         indexer_client = indexer.IndexerClient(algod_token, algod_address, headers)
#         indexer_client = indexer.IndexerClient(algod_token, algod_address, headers=purestake_token)
        indexer_client = indexer.IndexerClient("",algod_address, headers)
        print("return indexer_client")
        return indexer_client
    else:
        # TODO: return an instance of the client for sending transactions
        # Tutorial Link: https://developer.algorand.org/tutorials/creating-python-transaction-purestake-api/
        algod_address = "https://testnet-algorand.api.purestake.io/ps2"
#         algodclient = algod.AlgodClient(algod_token, algod_address, headers=purestake_token)
        algod_client = algod.AlgodClient(algod_token, algod_address, headers)
        print("return algod_client")
        return algod_client

#     return None






# TODO: You might want to adjust the first/last valid rounds in the suggested_params
#       See guide for details
# TODO: For each transaction, do the following:
#       - Create the Payment transaction 
#       - Sign the transaction
# TODO: Return a list of transaction id's
def send_tokens_algo( acl, sender_sk, txes):
#     params = acl.suggested_params

    
    
    sender_pk = account.address_from_private_key(sender_sk)
    tx_ids = []
    for i,tx in enumerate(txes):
        
        params = acl.suggested_params()
        receiver = tx['receiver_pk']
        amount = tx['amount']
        print(receiver)
        print(amount)
    
        # "Replace me with a transaction object"
        unsigned_tx = transaction.PaymentTxn(sender_pk, params, receiver, amount)
        
        # "Replace me with a SignedTransaction object"
        signed_tx = unsigned_tx.sign(sender_sk)

        try:
            print(f"Sending {tx['amount']} microalgo from {sender_pk} to {tx['receiver_pk']}" )
            
            # TODO: Send the transaction to the testnet
            # "Replace me with the tx_id"
            tx_id = acl.send_transaction(signed_tx)
            
            txinfo = wait_for_confirmation_algo(acl, txid=tx_id )
            print(f"Sent {tx['amount']} microalgo in transaction: {tx_id}\n" )
            tx_ids.append(tx_id)
        except Exception as e:
            print(e)

    return tx_ids








# Function from Algorand Inc.
def wait_for_confirmation_algo(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

##################################

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.exceptions import TransactionNotFound
import json
import progressbar


def connect_to_eth():
    IP_ADDR='3.23.118.2' #Private Ethereum
    PORT='8545'

    w3 = Web3(Web3.HTTPProvider('http://' + IP_ADDR + ':' + PORT))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0) #Required to work on a PoA chain (like our private network)
    w3.eth.account.enable_unaudited_hdwallet_features()
    if w3.isConnected():
        return w3
    else:
        print( "Failed to connect to Eth" )
        return None

def wait_for_confirmation_eth(w3, tx_hash):
    print( "Waiting for confirmation" )
    widgets = [progressbar.BouncingBar(marker=progressbar.RotatingMarker(), fill_left=False)]
    i = 0
    with progressbar.ProgressBar(widgets=widgets, term_width=1) as progress:
        while True:
            i += 1
            progress.update(i)
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
            except TransactionNotFound:
                continue
            break 
    return receipt


####################
def send_tokens_eth(w3,sender_sk,txes):
    sender_account = w3.eth.account.privateKeyToAccount(sender_sk)
    sender_pk = sender_account._address

    # TODO: For each of the txes, sign and send them to the testnet
    # Make sure you track the nonce -locally-
    
    print('\nsend_tokens_eth')
    
    tx_ids = []
    for i,tx in enumerate(txes):
        # Your code here
        print(i)
        print(tx['order_id'])
        tx_amount = tx['amount']
        tx_amounts = [tx_amount for _ in range(10)]
        receiver_pk = tx['receiver_pk']  
        tx_ids_inner = send_eth(sender_pk,sender_sk,receiver_pk,tx_amounts,w3)
        
#         for tx_id in tx_ids_inner:
#             ret = w3.eth.get_transaction(tx_id)
#             print("wait_for_confirmation_eth")
#             print(ret)
        
        tx_ids.append(tx_ids_inner)
        print('success')
        # continue

    return tx_ids


# def send_eth(sender_pk,sender_sk,receiver_pk,amounts,w3):
#     print(sender_pk)
#     print(sender_sk)
#     print(receiver_pk)
#     print(amounts)
    
#     starting_nonce = w3.eth.get_transaction_count(sender_pk,"pending")

#     tx_ids = []
#     for i,tx_amount in enumerate(amounts):
#         print(i)
#         tx_dict = {
#                     'nonce': starting_nonce+i, #Locally update nonce
#                     'gasPrice':w3.eth.gas_price,
#                     'gas': w3.eth.estimate_gas( { 'from': sender_pk, 'to': receiver_pk, 'data': b'', 'amount': tx_amount } ),
#                     'to': receiver_pk,
#                     'value': tx_amount,
#                     'data':b'' }
#         signed_txn = w3.eth.account.sign_transaction(tx_dict, sender_sk)
#         tx_id = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# #         wait_for_confirmation_algo(w3, tx_id)
#         print(tx_id.hex())
#         tx_ids.append(tx_id.hex())
    
#     print('exit')
#     return tx_ids


def send_eth(sender_pk,sender_sk,receiver_pk,amounts,w3):
    print(sender_pk)
    print(sender_sk)
    print(receiver_pk)
    print(amounts)
    
    starting_nonce = w3.eth.get_transaction_count(sender_pk,"pending")
    tx_dict = {
                'nonce': starting_nonce, #Locally update nonce
                'gasPrice':w3.eth.gas_price,
                'gas': w3.eth.estimate_gas( { 'from': sender_pk, 'to': receiver_pk, 'data': b'', 'amount': amounts[0] } ),
                'to': receiver_pk,
                'value': amounts[0],
                'data':b'' }
    
    signed_txn = w3.eth.account.sign_transaction(tx_dict, sender_sk)
    tx_id = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
#     wait_for_confirmation_algo(w3, tx_id)
    
    return tx_id.hex()




def eth_print():
    print()
    print()
    print()
    print('test')
    print()
    print()
    print()
