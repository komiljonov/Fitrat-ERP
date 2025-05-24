import requests
from decouple import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from data.lid.new_lid.signals import on_pre_save

base_url = config('TT_URL')
token = config('INTEGRATION_TOKEN')


class TimetrackerSinc:
    def __init__(self):

        print(token,base_url)

        self.INTEGRATION_TOKEN = token
        self.url = f"{base_url.rstrip('/')}/"

        self.headers = {
            "X-Integration-Token": self.INTEGRATION_TOKEN,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            raise_on_status=False,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_data(self):

        url = self.url + "employees"
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[GET] Error: {e}")
            return None

    def create_data(self, data):
        url = self.url + "employees"
        try:
            response = self.session.post(url, headers=self.headers, json=data, timeout=10)
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
