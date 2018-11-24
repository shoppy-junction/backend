import pandas as pd


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

def coords_from_bt(beacons):
    """
    beacons: a dictionary of beacon id mapped to signal strength
    """
    return min(beacons, key=lambda b: beacons[b])

    for beacon in beacons:
        pass
        
        


def main(filename):
    df = pd.read_csv(filename)
    grouped = df.sort_values(['userid', 'timestamp', 'rssi']).groupby(['userid', 'timestamp'])
    df = grouped.head(1)
    df['pos'] = df.apply(lambda row: BEACONS[row.beacon_id], axis=1)
    return df

if __name__ == "__main__":
    filename = "../data/fake_data.csv"
    print(main(filename))

