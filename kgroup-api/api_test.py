import requests

BEACONS_URL = "https://kesko.azure-api.net/files/beacons"
HEADERS = {"Ocp-Apim-Subscription-Key": "80a29c2c6af54807a3b1c57b6c78e032"}

def main():
    r = requests.post(BEACONS_URL, headers=HEADERS)
    print(r.text)



if __name__ == "__main__":
    main()
