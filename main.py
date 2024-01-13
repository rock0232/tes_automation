import json
import requests
from urllib.parse import urlparse, parse_qs

tes_url = "https://tes_api_dev.cloudd.live/api/v1/"
b2c_url = "https://uatapib2c.cloudd.live/api/"
b2c_api = "https://uatpanelb2c.cloudd.live/"
proxies = {
    "http": "http://36.67.45.71:8080",
}
sitename = "uatb2cclouddlive"

b2c_login = "Account/AppLogin"
manual_deposit01 = "B2CUser/ManualDepositGateway"
deposit_req = "user/deposit/req"


def login():
    logindata = {"UserName": "tes01", "Password": "Test@1234",
                 "RequestId": " ", "LoginWith": 1}
    r = requests.post(b2c_url + b2c_login, json=logindata, headers={"sitename": sitename}).json()
    access_token = (r["result"]["access_token"])
    return access_token


def manual_deposit():
    access_token = login()
    manual_dp_data = {
        "reqType": "upi",
        "amount": 0,
        "promoCode": ""
    }
    headers = {
        "Authorization": "bearer " + access_token,
        "sitename": sitename
    }
    r = requests.post(b2c_url + manual_deposit01, json=manual_dp_data, headers=headers).json()
    redirect_url = r["result"]["data"]["url"]
    parsed_url = urlparse(redirect_url)
    query_params = parse_qs(parsed_url.query)
    user_id = query_params.get('userId', [])[0]
    meta_data_raw = query_params.get('metaData', [])[0]
    meta_data_json = json.loads(meta_data_raw)
    json_obj = {"userId": user_id,
                "metaData": meta_data_json}
    return json_obj


def manual_deposit_req():
    data = manual_deposit()
    userid = data["userId"]
    promocode = data["metaData"]["PromoCode"]
    transaction_id = data["metaData"]["TransactionId"]
    placefrom = data["metaData"]["PlaceFrom"]
    amount = "215"
    reqType = "upi"
    headers = {"Content-Type": "application/json"}
    manualreq = {
        "reqType": reqType, "amount": amount, "userId": userid,
        "metaData": {"PromoCode": promocode, "TransactionId": transaction_id, "PlaceFrom": placefrom}}
    r = requests.post(tes_url + deposit_req, json=manualreq, headers=headers).json()
    print(r["data"]["account"]["name"])
    print(r["data"]["account"]["upiId"])
    print(r["data"]["account"]["priorityNumber"])
    print(r["data"]["account"]["depositReceiveAmount"])
    print(r["data"]["account"]["setLimit"])
    print(r["data"]["account"]["limit"])
    print(r["data"]["account"]["websiteId"])
    print(r["data"]["account"]["isOn"])
    print(r["data"]["account"]["type"])
    print(r["data"]["account"]["owner"])
    print(r["data"]["account"]["withdrawReceiveAmount"])
    print(r["data"]["account"]["totalWithLimit"])
    print(r["data"]["account"]["pendingWithLimit"])
    print(r["data"]["account"]["createdBy"])
    print(r["data"]["account"]["isActive"])
    print(r["data"]["account"]["createdAt"])
    print(r["data"]["account"]["updatedAt"])


if __name__ == '__main__':
    tes = "https://tes_api_dev.cloudd.live/api/v1/upload"
    headers = {
        'Content-Type': 'application/json'
    }
    # Cookie = {
    #     "_sp_srt_id.3603": "01327d18-b06d-49e4-8e06-3d2d7eb97ace.1701079989.3.1701148663.1701082564.18898fe5-1420-4871-b697-51de8025f759.0863b50d-3910-408b-9b3a-31444fa0e535...0"
    # }
    tesimg = 'Content-Disposition: form-data; name="image"; filename="payment.jpg"Content-Type: image/jpeg'
    # files = {
    #     'Content-Disposition': 'form-data',
    #     'name': "image",
    #     'image': open("payment.jpg", 'rb'),
    #     'Content-Type': 'image/jpeg'
    # }
    files = {
        'image': open("payment.jpg", 'rb')
    }
    test = requests.post(tes, json=files, headers=headers)
    print(test.text)

    # print(login())
    # manual_deposit()
    # manual_deposit_req()
