import random

from params import p
from params import g

# take no arguments and return a secret key (an integer in the range   1,... ,p )
# and a public key
def keygen():
    sk = random.randint(1, p)
    pk = pow(g, sk, p)
    return pk,sk

# take a public key,   h , and an integer   m  and return an El Gamal ciphertext
def encrypt(pk,m):
    r = random.randint(1, p)
    c1 = pow(g, r, p)
    # print(c1)
    c2 = ( (m % p) * pow(pk, r, p) ) % p
    # print(c2)
    return [c1, c2]

# take a private key,   a , and a ciphertext [  c1,c2 ] and return an integer m
def decrypt(sk,c):
    c1 = c[0]
    c2 = c[1]
    m = ( (c2 % p) * pow(c1, -sk, p) ) % p
    return m
