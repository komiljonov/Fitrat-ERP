import requests
from decouple import config

base_url = config('TT_URL')
token = config('INTEGRATION_TOKEN')

class TimetrackerSinc:
    def __init__(self):
        self.INTEGRATION_TOKEN = token
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
        try:
            response = requests.post(
                self.url + "employees/",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}

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
