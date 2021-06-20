import math

# Initially, the block reward was 50 BTC, and the reward halves every 210,000 blocks.
# Thus at Block 1 there were 50 BTC in circulation. At Block 2, there were 100 BTC etc


def num_BTC(b):
    c = float(0)
    reward = 50

    # ge the rounds of halving
    n = b // 210000

    # get the remaining number after last halving
    m = b % 210000

    while n > 0:
        c += 210000 * reward
        reward = reward/2
        n = n - 1

    c += m * reward
    return c
