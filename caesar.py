import string


def encrypt(key, plaintext):
    ciphertext = ""
    original_index = None
    new_index = None

    # iterate the chars in plaintext and do the cipher
    for element in plaintext.upper():
        original_index = string.ascii_uppercase.index(element)
        new_index = (original_index + key) % 26
        ciphertext += chr(ord('A') + new_index)

    return ciphertext


def decrypt(key, ciphertext):
    plaintext = ""
    original_index = None
    new_index = None

    # iterate the chars in plaintext and do the decipher
    for element in ciphertext.upper():
        original_index = string.ascii_uppercase.index(element)
        new_index = (original_index - key) % 26
        plaintext += chr(ord('A') + new_index)

    return plaintext
