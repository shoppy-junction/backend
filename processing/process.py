import pandas as pd

import math
import numpy


BEACONS = {
        1: (4.5,1),
        3: (17.3,3),
        4: (17.4,21.4),
        5: (16,15.2),
        6: (13.2,15.3),
        7: (10,15.31),
        8: (7,15.29),
        9: (4,15),
        10:(3,21),
        11:(3.5,6.5),
        12:(13,6)
        }

def triangulate(beacons):
    """
    beacons: a df of beacons with rssi values
    source: https://gist.github.com/kdzwinel/8235348
    """

    x1 = BEACONS[beacons.beacon_id1][0]
    y1 = BEACONS[beacons.beacon_id1][1]
    x2 = BEACONS[beacons.beacon_id2][0]
    y2 = BEACONS[beacons.beacon_id2][1]
    x3 = BEACONS[beacons.beacon_id3][0]
    y3 = BEACONS[beacons.beacon_id3][1]

    def d_from_rssi(rssi):
        return math.pow(10, (rssi+55)/-10.5)

    r1 = d_from_rssi(beacons.rssi1)
    r2 = d_from_rssi(beacons.rssi2)
    r3 = d_from_rssi(beacons.rssi3)

    S = (math.pow(x3, 2) - math.pow(x2, 2) + math.pow(y3, 2) - math.pow(y2, 2) + math.pow(r2, 2) - math.pow(r3, 2)) / 2
    T = (math.pow(x1, 2) - math.pow(x2, 2) + math.pow(y1, 2) - math.pow(y2, 2) + math.pow(r2, 2) - math.pow(r1, 2)) / 2
    y = ((T * (x2-x3)) - (S * (x2-x1))) / (((y1-y2)*(x2-x3)) - ((y3-y2)*(x2-x1)))
    x = ((y * (y1-y2)) - T) / (x2-x1)
    return x, y

def process(filename):
    df = pd.read_csv(filename)
    # take closest beacon
    # grouped = df.sort_values(['userid', 'timestamp', 'rssi']).groupby(['userid', 'timestamp'])
    # df = grouped.tail(1)
    # df['pos'] = df.apply(lambda row: BEACONS[row.beacon_id], axis=1)

    # take triangulated value
    top3 = df.groupby(['timestamp', 'userid'])['rssi', 'beacon_id'] \
            .apply(lambda x: x.nlargest(3, columns=['rssi']) \
            .reset_index(drop=True)[['beacon_id', 'rssi']]) \
            .unstack()[['beacon_id', 'rssi']]

    top3.columns = [col[0] + str(1+col[1]) for col in top3.columns.values]

    df = top3.apply(triangulate, axis=1).reset_index()
    df['x'], df['y'] = df.apply(lambda x: x[0][0], axis=1), df.apply(lambda x: x[0][1], axis=1)
    return df.set_index(['userid', 'timestamp'])[['x', 'y']]

if __name__ == "__main__":
    filename = "../data/fake_data.csv"
    df = process(filename)
    print(df)
    # df[['userid', 'timestamp', 'pos']].to_csv('fake_xy_for_michael.csv', index=False)
    df.to_csv('../data/processed_output.csv')


