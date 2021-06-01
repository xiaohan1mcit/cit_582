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

    m_byte = m.encode('utf-8')
    m_hash = hashlib.sha256(m_byte)
    m_hex = m_hash.hexdigest()
    z = int(m_hex, 16)
    print("z")
    print(z)

    # generator
    G = secp256k1.G
    # order of generator
    n = secp256k1.q
    print("n")
    print(n)

    # private signing key
    d = random.randint(1, n)
    print("d")
    print(d)

    # public verification key Q
    public_key = d*G
    print("public_key")
    print(public_key.x)
    print(public_key.y)

    # generate random nonce k
    k = random.randint(0, 10000)
    print("k")
    print(k)

    # generate x1, y1
    xy = k*G
    print("xy")
    print(xy.x)
    print(xy.y)

    # generate signature

    # generate r
    r = pow(xy.x, 1, n)
    print("r")
    print(r)

    # generate z

    # generate s
    s = ( pow(k, -1, n) * ((z + 2*d) % n) ) % n
    print("s")
    print(s)

    assert isinstance(public_key, point.Point)
    assert isinstance(r, int)
    assert isinstance(s, int)
    return (public_key, [r, s])
