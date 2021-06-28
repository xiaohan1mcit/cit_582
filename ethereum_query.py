import web3
from web3 import Web3
from hexbytes import HexBytes

IP_ADDR = '18.188.235.196'
PORT = '8545'

w3 = Web3(Web3.HTTPProvider('http://' + IP_ADDR + ':' + PORT))

# This line will mess with our autograders, but might be useful when debugging
# if w3.isConnected():
#     print("Connected to Ethereum node")
# else:
#     print("Failed to connect to Ethereum node!")


# The input variable 'tx' in the get_transaction() function
# will be the hash value of a transaction on the ethereum blockchain.
# The function itself should return the dictionary object that holds all of the details/info for that transaction.
def get_transaction(tx):
    # tx = {}
    tx = w3.eth.get_transaction(tx)
    return tx


# Return the gas price used by a particular transaction,
#   tx is the transaction
def get_gas_price(tx):
    trnas = get_transaction(tx)
    gas_price = trnas['gasPrice']
    return gas_price


def get_gas(tx):
    hash_tx = tx['hash']
    gas = w3.eth.get_transaction_receipt(hash_tx)['gasUsed']
    return gas


def get_transaction_cost(tx):
    tx_cost = get_gas_price(tx) * get_gas(tx)
    return tx_cost


def get_block_cost(block_num):
    block_cost = 0

    tx_num = w3.eth.get_block_transaction_count(block_num)
    # print(tx_num)

    tx_list = w3.eth.get_block(block_num, False)['transactions']
    # print(tx_list)

    for i in range(tx_num):
        tx = get_transaction(tx_list[i])
        tx_cost = get_transaction_cost( tx )
        # print(tx)
        # print(tx_cost)
        block_cost += tx_cost

    return block_cost


# Return the hash of the most expensive transaction
def get_most_expensive_transaction(block_num):
    max_tx = HexBytes('0xf7f4905225c0fde293e2fd3476e97a9c878649dd96eb02c86b86be5b92d826b6')  # YOUR CODE HERE
    max_cost = 0
    # print(max_tx)

    tx_num = w3.eth.get_block_transaction_count(block_num)
    # print(tx_num)

    tx_list = w3.eth.get_block(block_num, False)['transactions']
    # print(len(tx_list))

    for i in range(tx_num):
        tx = get_transaction( tx_list[i] )
        tx_cost = get_transaction_cost(tx)
        if tx_cost > max_cost :
            # print(i)
            # print(tx_cost)
            max_tx = HexBytes(tx['hash'])
            max_cost = tx_cost
            # print(max_tx)

    return max_tx
