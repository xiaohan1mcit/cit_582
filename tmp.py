from zksk import DLRep, Secret, utils

G, H = utils.make_generators(num=2, seed=42)
r1 = Secret(utils.get_random_num(bits=128))
r2 = Secret(utils.get_random_num(bits=128))

m=1
C1 = r1.value * G
C2 = m * G + r1.value * H

D1 = r2.value * G
D2 = m*G + r2.value*H

stmt = DLRep(C1, r1*G)

import code
code.interact(local=locals())
