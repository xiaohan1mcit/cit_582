# !/usr/bin/python3
from algosdk.v2client import algod
from algosdk import mnemonic, account, encoding
from algosdk import transaction

# Connect to Algorand node maintained by PureStake
# Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
# algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
headers = {
    "X-API-Key": algod_token,
}


# convert passphrase to secret key
mnemonic_secret = "such chapter crane ugly uncover fun kitten duty culture giant skirt reunion pizza pill web monster upon dolphin aunt close marble dune kangaroo ability merit"
sk = mnemonic.to_private_key(mnemonic_secret)
pk = mnemonic.to_public_key(mnemonic_secret)




# generate an account
# private_key, address = account.generate_account()
print("Private key:", sk)
print("Address:", pk)

# check if the address is valid
if encoding.is_valid_address(pk):
    print("The address is valid!")
else:
    print("The address is invalid.")







# Status: Code 200 success: "ICCLLPTDWKCXOZJOOUGRMUAZSZH775D5KTGXKEW6ZHDV2LG63L2A"



acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000  # https://developer.algorand.org/docs/features/accounts/#minimum-balance










# Your function should create a transaction that sends “amount” microalgos to the account
# given by “receiver_pk” and submit the transaction to the Algorand Testnet.
# Your function should return the address of the sender (“sender_pk”)
# as well as the id of the resulting transaction (“txid”) as it appears on the Testnet blockchain.
def send_tokens(receiver_pk, tx_amount):
    params = acl.suggested_params()
    gen = params.gen
    gen_hash = params.gh
    first_valid_round = params.first
    last_valid_round = params.last
    tx_fee = params.min_fee
    send_amount = 1

    # Your code here
    # create the transaction
    # txn = transaction.PaymentTxn(pk, params, receiver_pk, tx_amount)
    txn = transaction.PaymentTxn(pk, tx_fee, first_valid_round, last_valid_round, gen_hash, receiver_pk, tx_amount,
                                 flat_fee=True)


    # sign it
    stx = txn.sign(sk)

    # send it
    txid = acl.send_transaction(stx)

    sender_pk = pk

    return sender_pk, txid


# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
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
