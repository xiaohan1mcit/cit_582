import hashlib
import random

from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair

from fastecdsa import curve, ecdsa, keys, point
from hashlib import sha256


# takes in a single message m, and, creates a new key-pair for an ECDSA signature scheme,
# return the ECDSA public key and the signature
# an ECDSA signature consists of 2 integers, r,s. These should be returned as a list of length two
# Thus your function, “sign,” should return two elements,
# a public key and a list of length two that holds the two components of the signature.
# Your function should use the curve SECP256K1 (the “Bitcoin” curve) and the hash functions SHA256.
def sign(m):

    print("m")
    print(type(m))
    print(m)

    # # generator
    # G = secp256k1.G
    # # order of generator
    # n = secp256k1.q
    # # private signing key
    # d = random.randint(1, n)
    # # public verification key Q
    # public_key = d*G
    # # generate random nonce k
    # k = random.randint(0, 10000)
    # # generate x1, y1
    # xy = k*G

    d, public_key = keys.gen_keypair(curve.secp256k1)
    print("key pair")
    print(d)
    print(public_key)

    # generate signature

    rs = ecdsa.sign(m, d)
    print("r")
    print(rs[0])
    print("s")
    print(rs[1])
    r = rs[0]
    s = rs[1]

    # generate r
    # r = xy.x % n

    # generate z
    # m_byte = m.encode('utf-8')
    # print("m_byte")
    # print(m_byte)
    # m_hash = hashlib.sha256(m_byte)
    # print("m_hash")
    # print(m_hash)
    # m_hex = m_hash.hexdigest()
    # print("m_hex")
    # print(m_hex)
    # z = int(m_hex, 16)
    # print("z")
    # print(z)

    # generate s
    # s = ( pow(k, -1, n) * ((z + 2*d) % n) ) % n
    # print("s")
    # print(s)

    assert isinstance(public_key, point.Point)
    assert isinstance(r, int)
    assert isinstance(s, int)
    return (public_key, [r, s])
