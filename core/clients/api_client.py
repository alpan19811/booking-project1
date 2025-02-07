import requests
import os
from dotenv import load_dotenv
from core.settings.environments import Environment
from core.clients.endpoints import Endpoints
from core.settings.config import Users, Timeouts
from requests.auth import HTTPBasicAuth
import allure

load_dotenv()

class APIClient:
    def __init__(self):
        environment_str = os.getenv('ENVIRONMENT')
        try:
            environment = Environment[environment_str]
        except KeyError:
            raise ValueError(f'Unsupported environment value: {environment_str}')

        self.base_url = self.get_base_url(environment)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
    })

    def get_base_url(self, environment: Environment) -> str:
        if environment == Environment.TEST:
            return os.getenv('TEST_BASE_URL')
        elif environment == Environment.PROD:
            return os.getenv('PROD_BASE_URL')
        else:
            raise ValueError(f"Unsupported environment: {environment}")

    def get(self, endpoint, params=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.session.headers, params=params)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def post(self, endpoint, data=None, status_code=200):
        url = self.base_url + endpoint
        response = requests.post(url, headers=self.session.headers, json=data)
        if status_code:
            assert response.status_code == status_code
        return response.json()

    def ping(self):
        with allure.step('Ping api client'):
            url = f"{self.base_url}/{Endpoints.PING_ENDPOINT}"
            response = self.session.get(url)
            response.raise_for_status()
        with allure.step('Assert status code'):
            assert response.status_code == 201, f"Expected status 201 but got {response.status_code}"
        return response.status_code

    def auth(self):
        with allure.step('Getting authenticate'):
            url = f"{self.base_url}/{Endpoints.AUTH_ENDPOINT.value}"
            payload = {"username": Users.USERNAME.value, "password": Users.PASSWORD.value}

            timeout_value = Timeouts.TIMEOUT.value

            response = self.session.post(url, json=payload, timeout=timeout_value)
            response.raise_for_status()

        if response.status_code != 200:
            raise ValueError(f"Failed to authenticate, status code: {response.status_code}")

        token = response.json().get("token")
        if not token:
            raise ValueError("Authentication failed: token not received")

        self.session.headers.update({"Authorization": f"Bearer {token}"})
        print(f"Token for authorization: {token}")

    def get_booking_by_id(self, booking_id):
        with allure.step(f'Getting booking with ID {booking_id}'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT}/{booking_id}"
            response = self.session.get(url, timeout=Timeouts.TIMEOUT.value)
            response.raise_for_status()

        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"

        with allure.step('Returning booking data'):
            return response.json()

    def delete_booking(self, booking_id, token=None):
        with allure.step('Deleting booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT.value}/{booking_id}"

            print(f"Token for authorization: {token}")

            headers = {}
            if token:
                headers['Authorization'] = f'Bearer {token}'

            response = self.session.delete(url, headers=headers or None)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 201, f"Expected status 201 but got {response.status_code}"
        return response.status_code == 201

    def create_booking(self, booking_data):
        with allure.step('Creating booking'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT}"
            response = self.session.post(url, json=booking_data)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

    def get_booking(self, params=None):
        with allure.step('Getting object with bookings'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 201 but got {response.status_code}"
        return response.json()


    def update_booking(self, booking_id, booking_data):
        with allure.step(f'Updating booking with ID {booking_id}'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT}/{booking_id}"
            response = self.session.put(url, json=booking_data)
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        with allure.step('Returning updated booking data'):
            return response.json()


    def partial_update_booking(self, booking_id, booking_data):
        with allure.step(f'Partially updating booking with ID {booking_id}'):
            url = f"{self.base_url}{Endpoints.BOOKING_ENDPOINT}/{booking_id}"
            response = self.session.patch(url, json=booking_data, auth=HTTPBasicAuth(Users.USERNAME, Users.PASSWORD))
            response.raise_for_status()
        with allure.step('Checking status code'):
            assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        return response.json()

if __name__ == "__main__":
    from core.settings.config import Users

    client = APIClient()
    client.auth()
    booking_id = 1
    result = client.delete_booking(booking_id)
    if result:
        print(f"Booking with ID {booking_id} was successfully deleted.")
    else:
        print(f"Failed to delete booking with ID {booking_id}.")




