import requests
from decouple import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

base_url = config("TT_URL")
token = config("INTEGRATION_TOKEN")


class HrPulseIntegration:
    def __init__(self):

        print(token)

        self.INTEGRATION_TOKEN = token
        self.url = f"{base_url.rstrip('/')}/"
        print(self.url)

        self.headers = {
            "X-Integration-Token": self.INTEGRATION_TOKEN,
            "Accept": "application/json",
            "Content-Type": "application/json",
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

    def archive_employee(self, employee_id):
        url = self.url + f"employees/{employee_id}"
        try:
            response = self.session.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            if response.text:  # Only try to decode if there's something
                return response.json()
            return {"message": "Archived successfully without response body."}
        except requests.exceptions.RequestException as e:
            print(f"[DELETE] Error: {e}")

    def upload_tt_foto(self, django_file):
        import mimetypes

        url = "https://api.tictac.sector-soft.ru/api/files/upload"
        try:
            django_file.open("rb")
            mime_type, _ = mimetypes.guess_type(django_file.name)

            files = {
                "file": (
                    django_file.name,
                    django_file.file,
                    mime_type or "application/octet-stream",
                )
            }

            headers = {
                k: v for k, v in self.headers.items() if k.lower() != "content-type"
            }

            response = self.session.post(url, headers=headers, files=files, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[POST] Error: {e}")
            if e.response is not None:
                print("Response content:", e.response.text)
            return None
        finally:
            django_file.close()

    def create_data(self, data):
        url = self.url + "employees/create"
        try:
            response = self.session.post(
                url, headers=self.headers, json=data, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[POST] Error: {e}")
            return None

    def create_filial(self, data):
        url = self.url + "filials"
        try:
            response = self.session.post(
                url, headers=self.headers, json=data, timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"[POST] Error: {e}")
            return None

    def get_filial(self, filial):
        url = self.url + "filials"
        try:
            response = self.session.get(
                url, headers=self.headers, params={"q": filial}, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[GET] Error: {e}")
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
