import requests
from decouple import config

base_url = config('TT_URLS')

class TimetrackerSinc:
    def __init__(self):
        self.INTEGRATION_TOKEN = "abcd1234"
        self.url = f"{base_url}/"
        self.headers = {
            "X-Internal-Auth": self.INTEGRATION_TOKEN,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_data(self):
        url = self.url + "employees"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[GET] Error: {e}")
            return None

    def create_data(self, data):
        url = self.url + "employees"
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[POST] Error: {e}")
            return None

    def retrieve_data(self, employee_id):
        url = self.url + f"employees/{employee_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[GET by ID] Error: {e}")
            return None

    def update_data(self, employee_id, data):
        url = self.url + f"employees/{employee_id}"
        try:
            response = requests.put(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[PUT] Error: {e}")
            return None
