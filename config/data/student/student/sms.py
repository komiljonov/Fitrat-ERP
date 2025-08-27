import hashlib
import os
from random import randint
from sys import stderr
import time

from dotenv import load_dotenv
from icecream import ic
from requests import post

load_dotenv()


class SayqalSms:
    def __init__(self):
        self.username = os.getenv("SAYQAL_USERNAME")
        self.token = os.getenv("SAYQAL_TOKEN")

        assert (
            self.username is not None
        ), "Environment variable SAYQAL_USERNAME is not set"

        assert self.token is not None, "Environment variable SAYQAL_TOKEN is not set"

        self.url = "https://routee.sayqal.uz/sms/"

    def generateToken(self, method: str, utime: int):

        access = f"{method} {self.username} {self.token} {utime}"
        token = hashlib.md5(access.encode()).hexdigest()

        return token

    def fixNumber(self, number: str):
        if number.startswith("+"):
            return number[1:]

    def send_sms(self, number: str, message: str):

        utime = int(time.time())

        token = self.generateToken("TransmitSMS", utime)

        print(token)

        number = self.fixNumber(number)

        print(number, file=stderr)

        url = self.url + "TransmitSMS"
        data = {
            "utime": utime,
            "username": self.username,
            "service": {"service": 1},
            "message": {
                "smsid": randint(111111, 999999),
                "phone": number,
                "text": message,
            },
        }

        print(token, data)

        response = post(url, json=data, headers={"X-Access-Token": token})

        ic("Sms response", data, response.json())

        return response.json()
