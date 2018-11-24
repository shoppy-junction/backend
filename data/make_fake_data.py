import pandas as pd
import random

BEACONS = {
        1: (4,1),
        3: (17,3),
        4: (17,21),
        5: (16,15),
        6: (13,15),
        7: (10,15),
        8: (7,15),
        9: (4,15),
        10:(3,21),
        11:(3,6),
        12:(13,6)
        }
l = []
for i in range(500):

    for j in BEACONS:
        d = {"userid": 0, "timestamp":1543020253 + i, "beacon_id": j, "rssi":random.randint(-90, -50)}
        l += [d]

df = pd.DataFrame(l)
print(df)

df.to_csv("fake_data.csv", index=False)
