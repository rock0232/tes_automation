import pytest
import requests as req
import json
from urllib.parse import urlparse, parse_qs
import random
import string
from Utilities import Logger


class Test_login:
    logger = Logger.logen()
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
    deposit_submit = "user/deposit/submit"
    cred = {
        "admin": {
            "userId": "admin",
            "password": "admin"
        },
        "vendor": {
            "userId": "spvendor",
            "password": "Test@123"
        },
        "agent": {
            "userId": "ar_uat",
            "password": "Abc@1234"
        }
    }

    def generate_random_string(self, length, dtype):
        if dtype == int:
            digits = string.digits
            random_string = ''.join(random.choice(digits) for i in range(length))
        else:
            letters_and_digits = string.ascii_letters + string.digits
            random_string = ''.join(random.choice(letters_and_digits) for i in range(length))
        return random_string

    @pytest.fixture()
    def admin_login(self):
        json_data = {"userId": self.cred["admin"]["userId"], "password": self.cred["admin"]["userId"],
                     "userType": "admin"}
        r = req.post(url=self.tes_url + "admin/login", json=json_data).json()
        return r["data"]["token"]

    @pytest.fixture()
    def vendor_login(self):
        json_data = {
            "userId": self.cred["vendor"]["userId"], "password": self.cred["vendor"]["userId"], "userType": "vendor"}
        r = req.post(url=self.tes_url + "admin/login", json=json_data).json()
        return r["data"]["token"]

    @pytest.fixture()
    def agent_login(self):
        json_data = {"userId": self.cred["agent"]["userId"], "password": self.cred["agent"]["password"],
                     "userType": "agent"}
        r = req.post(url=self.tes_url + "admin/login", json=json_data).json()
        return r["data"]["token"]

    def test_login_001(self):
        r = req.get("https://tes_api_dev.cloudd.live/api/v1/").json()
        assert "Running" in r["message"]

    def test_b2clogin(self):
        logindata = {"UserName": "tes01", "Password": "Test@1234",
                     "RequestId": " ", "LoginWith": 1}
        r = req.post(self.b2c_url + self.b2c_login, json=logindata, headers={"sitename": self.sitename}).json()
        access_token = (r["result"]["access_token"])
        assert "access_token" in r["result"]
        self.logger.info("User Logged in successfully")
        return "bearer " + access_token

    def test_manualdeposit(self):
        access_token = Test_login.test_b2clogin(self)
        manual_dp_data = {
            "reqType": "upi",
            "amount": 0,
            "promoCode": ""
        }
        headers = {
            "Authorization": access_token,
            "sitename": self.sitename
        }
        reqs = req.post(self.b2c_url + self.manual_deposit01, json=manual_dp_data, headers=headers)
        assert reqs.status_code == 200
        r = reqs.json()
        redirect_url = r["result"]["data"]["url"]
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        user_id = query_params.get('userId', [])[0]
        meta_data_raw = query_params.get('metaData', [])[0]
        meta_data_json = json.loads(meta_data_raw)
        json_obj = {"userId": user_id,
                    "metaData": meta_data_json}
        assert r["isSuccess"] == True
        self.logger.info("Transaction initialize without enter amount")
        return json_obj

    def test_deposit_req(self):
        data = Test_login.test_manualdeposit(self)
        userid = data["userId"]
        promocode = data["metaData"]["PromoCode"]
        transaction_id = data["metaData"]["TransactionId"]
        placefrom = data["metaData"]["PlaceFrom"]
        amount = Test_login.generate_random_string(self, 3, int)
        reqType = "upi"
        headers = {"Content-Type": "application/json"}
        manualreq = {
            "reqType": reqType, "amount": amount, "userId": userid,
            "metaData": {"PromoCode": promocode, "TransactionId": transaction_id, "PlaceFrom": placefrom}}
        reqs = req.post(self.tes_url + self.deposit_req, json=manualreq, headers=headers)
        print(reqs.text)
        assert reqs.status_code == 200
        self.logger.info("Manual payment details was send")
        r = reqs.json()
        rdata = {
            "depositId": r["data"]["_id"],
            "ReceiverType": r["data"]["account"]["owner"],
            "ReceiverName": r["data"]["account"]["name"],
            "upiId": r["data"]["account"]["upiId"],
            "priorityNumber": r["data"]["account"]["priorityNumber"],
            "createdBy": r["data"]["account"]["createdBy"],
            "assignedTo": r["data"]["assignedTo"],
            "traId": r["data"]["traId"],
            "websiteId": r["data"]["websiteId"],
            "endUserId": r["data"]["userDetails"]["endUserId"],
            "uniqueId": r["data"]["userDetails"]["uniqueId"],
            "websitename": r["data"]["userDetails"]["websiteId"]["name"]
        }
        return rdata

    def test_submit_deposit(self):
        data = Test_login.test_deposit_req(self)
        utr = Test_login.generate_random_string(self, 12, string)
        data["image"] = {}
        data["paymentSS"] = "https://tes_api_dev.cloudd.live/api/v1/images/1701321921422_AAdhar.jpg"
        data["transactionId"] = utr
        r = req.post(url=self.tes_url + self.deposit_submit, json=data)
        assert r.status_code == 200
        self.logger.info(
            "Transaction successfully Created, \n"
            "Transaction Request Was Assigned to %s \n"
            "Assignee Name is %s \n"
            "Assignee Account Details is %s \n"
            "Assignee Account Priority NUmber is %s", data["ReceiverType"], data["ReceiverName"], data["upiId"],
            data["priorityNumber"],
        )
        return data

    def test_getrequest(self, admin_login):
        data = Test_login.test_submit_deposit(self)
        admin_token = admin_login
        headers = {
            "Content-Type": "application/json",
            "Authorization": admin_token
        }
        rbody = {
            "page": 1,
            "limit": 50000,
            "statusFilter": "",
            "search": None,
            "reqTypeFilter": None
        }
        r = req.post(url=self.tes_url + "admin/deposit/get/all", headers=headers, json=rbody)
        filtered_data = {
            "deposit_data": [item for item in r.json()["data"]["deposit_data"] if
                             item.get("traId") == data["traId"]]
        }
        assert filtered_data["deposit_data"][0]["traId"] == data["traId"], \
            self.logger.info("Transaction Data Not Retrieved from Deposit Queue")
