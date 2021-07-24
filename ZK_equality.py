from zksk import Secret, DLRep
from zksk import utils

def ZK_equality(G,H):
  
    r1 = Secret(utils.get_random_num(bits=128))
    r2 = Secret(utils.get_random_num(bits=128))
    m=1

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    C1 = r1.value * G
    C2 = m * G + r1.value * H

    D1 = r2.value * G
    D2 = m*G + r2.value*H

    #Generate a NIZK proving equality of the plaintexts
    stmt = DLRep(C1, r1.value*G) & DLRep(C2, r1.value*H + m*G) & DLRep(D1, r2.value*G) & DLRep(D2, r2.value*H+m*G)
    zk_proof = stmt.prove()

    #Return two ciphertexts and the proof
    return (C1,C2), (D1,D2), zk_proof
