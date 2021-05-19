import hashlib
import os
import random
import string


def hash_collision(k):
    # check k
    if not isinstance(k, int):
        print("hash_collision expects an integer")
        return (b'\x00', b'\x00')
    if k < 0:
        print("Specify a positive number of bits")
        return (b'\x00', b'\x00')

    # Collision finding code goes here
    x = b'\x00'
    y = b'\x00'

    # generate a random string
    letters = string.ascii_letters
    str_x_random = ''.join(random.choice(letters) for i in range(10))

    # convert the str to bytecode and assign it to x
    byte_str_x_random = str_x_random.encode('utf-8')
    x = byte_str_x_random

    # get the sha256 hash value of the byte code
    result_x_random = hashlib.sha256(byte_str_x_random)
    hex_result_x_random = result_x_random.hexdigest()

    # get last k digits of the hash
    last_k = hex_result_x_random[-k:]

    # use a while loop to find y with brute force
    while True:
        # generate a random string
        str_y_random = ''.join(random.choice(letters) for i in range(10))

        # convert the str to bytecode and assign it to x
        byte_str_y_random = str_y_random.encode('utf-8')

        # get the sha256 hash value of the byte code
        result_y_random = hashlib.sha256(byte_str_y_random)
        hex_result_y_random = result_y_random.hexdigest()

        # compare the last k digits
        if (hex_result_y_random[-k:] == last_k) :
            y = byte_str_y_random
            break

    return (x, y)
