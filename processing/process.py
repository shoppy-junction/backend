import pandas as pd
import math
import numpy as np


BEACONS = {
        1: (4.5,1.1),
        3: (17.3,3.2),
        4: (17.4,21.42),
        5: (16,15.26),
        6: (13.2,15.34),
        7: (10,15.31),
        8: (7,15.29),
        9: (4,15),
        10:(3,21.05),
        11:(3.5,6.5),
        12:(13,6)
        }

def closest_beacon(row):
    if row.beacon_id in BEACONS:
        return BEACONS[row.beacon_id]
    else:
        return None

def triangulate(beacons):
    """
    beacons: a df of beacons with rssi values
    source: https://gist.github.com/kdzwinel/8235348
    """

    if len(beacons) != 6:
        return None

    try:
        x1 = BEACONS[beacons.beacon_id1][0]
        y1 = BEACONS[beacons.beacon_id1][1]
        x2 = BEACONS[beacons.beacon_id2][0]
        y2 = BEACONS[beacons.beacon_id2][1]
        x3 = BEACONS[beacons.beacon_id3][0]
        y3 = BEACONS[beacons.beacon_id3][1]
    except KeyError as e:
        print('beacon not found:', e)
        return None

    def d_from_rssi(rssi):
        return math.pow(10, (rssi+55)/-10.5)

    r1 = d_from_rssi(beacons.rssi1)
    r2 = d_from_rssi(beacons.rssi2)
    r3 = d_from_rssi(beacons.rssi3)

    S = (math.pow(x3, 2)-math.pow(x2, 2)+math.pow(y3, 2)-math.pow(y2, 2)+math.pow(r2, 2)-math.pow(r3, 2))/2
    T = (math.pow(x1, 2)-math.pow(x2, 2)+math.pow(y1, 2)-math.pow(y2, 2)+math.pow(r2, 2)-math.pow(r1, 2))/2
    try:
        y = ((T * (x2-x3)) - (S * (x2-x1))) / (((y1-y2)*(x2-x3)) - ((y3-y2)*(x2-x1)))
    except ZeroDivisionError:
        return None
    x = ((y * (y1-y2)) - T) / (x2-x1)
    return x, y

def process(filename):
    df = pd.read_csv(filename)
    # take closest beacon
    grouped = df.sort_values(['userid', 'timestamp', 'rssi']).groupby(['userid', 'timestamp'])
    df = grouped.tail(1)
    pos = df.set_index(['userid', 'timestamp']).apply(closest_beacon, axis=1)
    df = df.set_index(['userid', 'timestamp'])
    df['x'], df['y'] = pos.apply(lambda x: x[0]), pos.apply(lambda x: x[1])
    df = df[['x', 'y']]

    # add some noise to make data look nicer
    mu, sigma = 0, 2
    noise = np.random.normal(mu, sigma, [len(df), 2])
    print(noise)
    df = df + noise
    return df

    """ triangulation shit
    # take triangulated value
    top3 = df.groupby(['timestamp', 'userid'])['rssi', 'beacon_id'] \
            .apply(lambda x: x.nlargest(3, columns=['rssi']) \
            .reset_index(drop=True)[['beacon_id', 'rssi']]) \
            .unstack()[['beacon_id', 'rssi']]

    top3.columns = [col[0] + str(1+col[1]) for col in top3.columns.values]

    #print(top3)
    df = top3.apply(triangulate, axis=1).reset_index()
    #print(df)
    df.fillna(value=pd.np.nan, inplace=True)
    df.dropna(inplace=True)
    df['x'], df['y'] = df.apply(lambda x: x[0][0], axis=1), df.apply(lambda x: x[0][1], axis=1)
    return df.set_index(['userid', 'timestamp'])[['x', 'y']]
    """

if __name__ == "__main__":
    filename = "../data/fake_data.csv"
    df = process(filename)
    print(df)
    df.to_csv('../data/processed_output.csv')


