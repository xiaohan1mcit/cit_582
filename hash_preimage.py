import hashlib
import os
import string
import random


def hash_preimage(target_string):

    # check it target_string only contain 0 or 1
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return

    nonce = b'\x00'
    target_len = len(target_string)
    letters = string.ascii_letters

    # iterate in while loop until get a matching bytecode
    while True:
        # generate a random string
        str = ''.join(random.choice(letters) for i in range(10))

        # convert the str to bytecode and assign it to x
        str_byte = str.encode('utf-8')

        # get the sha256 hash value of the byte code in binary
        str_sha = hashlib.sha256(str_byte)
        str_sha_hex = str_sha.hexdigest()
        str_sha_bin = (bin(int(str_sha_hex, 16))[2:]).zfill(256)

        # compare str_sha_bin with target_string
        if ( str_sha_bin[-target_len:] == target_string ):
            nonce = str_byte
            break

    return( nonce )
