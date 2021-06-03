import hashlib


# In this homework you are asked to write a very simple blockchain.
# At its core, the blockchain is implemented as a linked list.

# Each block, as can be seen in the Block class we’ve defined for you,
# includes an index, a timestamp, a content and the hash of the previous block. The class defines the genesis block.


class Block:
    def __init__(self, index, timestamp, content, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.content = content
        self.previous_hash = previous_hash
        self.hash = self.calc_hash()

    def calc_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode('utf-8') +
                   str(self.timestamp).encode('utf-8') +
                   str(self.content).encode('utf-8') +
                   str(self.previous_hash).encode('utf-8'))
        return sha.hexdigest()


M4BlockChain = []

from datetime import datetime


# defines the genesis block
def create_genesis_block():
    return Block(0, datetime.now(), "Genesis Block", "0")


M4BlockChain.append(create_genesis_block())


# define a function that generates the next blocks
# where the index of each block is the index of the previous block plus one,
# the timestamp is the current time,
# and the content is a string “this is block i” where i is the index of the block.
def next_block(last_block):
    content = 'this is block ' + str(last_block.index + 1)
    return Block( (last_block.index + 1), datetime.now(), content, last_block.hash)


# append 5 blocks to the blockchain
def app_five(block_list):
    for i in range(5):
        block_list.append( next_block( block_list[-1] ) )
        # print(block_list[-1].index)
        # print(block_list[-1].timestamp)
        # print(block_list[-1].content)
        # print(block_list[-1].previous_hash)
        # print(block_list[-1].hash)
        # print("\n")
