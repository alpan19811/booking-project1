import allure
import pytest
import requests

from core.clients import api_client


@allure.feature('Test Ping')
@allure.story('Test connection')
def test_ping(api_client):
    status_code = api_client.ping()
    assert status_code == 201, f"Expected status 201 but got {status_code}"

@allure.feature('Test Ping')
@allure.story('Test server unavailability')
def test_ping_server_unavailable(api_client, mocker):
    mocker.patch.object(api_client.session, 'get', side_effect=Exception("Server unavailability"))
    with pytest.raises(Exception, match="Server unavailability"):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test wrong HTTP method')
def test_ping_wrong_method(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code =405
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match="Expected status 201 but got 405"):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test test error')
def test_ping_internal_server_error(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code =500
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match="Expected status 201 but got 500"):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test wrong URL')
def test_ping_not_found(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code =404
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match="Expected status 201 but got 404"):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test connection with different success code')
def test_ping_wrong_method(api_client, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code =200
    mocker.patch.object(api_client.session, 'get', return_value=mock_response)
    with pytest.raises(AssertionError, match="Expected status 201 but got 200"):
        api_client.ping()


@allure.feature('Test Ping')
@allure.story('Test timeout')
def test_ping_timeout(api_client, mocker):
    mocker.patch.object(api_client.session, 'get', side_effect=requests.Timeout)
    with pytest.raises(requests.Timeout):
        api_client.ping()


@allure.feature('Create booking')
@allure.story('Create booking with valid data')
def test_create_booking_success(api_client, generate_random_booking_data):
    with allure.step('Prepare booking data'):
        booking_data = generate_random_booking_data

    with allure.step('Send POST request to create booking'):
        response = api_client.create_booking(booking_data)

    with allure.step('Check response status code'):
        assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"

    with allure.step('Check booking data in response'):
        response_data = response.json()
        assert "booking" in response_data, "Booking ID is missing in the response"
        assert response_data["booking"]["firstname"] == booking_data["firstname"]
        assert response_data["booking"]["lastname"] == booking_data["lastname"]
        assert response_data["booking"]["totalprice"] == booking_data["totalprice"]
        assert response_data["booking"]["depositpaid"] == booking_data["depositpaid"]
        assert response_data["booking"]["bookingdates"] == booking_data["bookingdates"]
        assert response_data["booking"]["additionalneeds"] == booking_data["additionalneeds"]


@allure.feature('Create booking')
@allure.story('Create booking with invalid data')
def test_create_booking_invalid_data(api_client):
    booking_data = {
        "firstname": "",
        "lastname": "Doe",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2023-10-01",
            "checkout": "2023-10-05"
        },
        "additionalneeds": "Breakfast"
    }

    with allure.step('Send POST request with invalid data'):
        response = api_client.create_booking(booking_data)

    with allure.step('Check response status code'):
        assert response.status_code == 400, f"Expected status 200 but got {response.status_code}"


@allure.feature('Create booking')
@allure.story('Create booking with server error')
def test_create_booking_server_error(api_client, mocker):
    booking_data = {
        "firstname": "",
        "lastname": "Doe",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2023-10-01",
            "checkout": "2023-10-05"
        },
        "additionalneeds": "Breakfast"
    }
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mocker.patch.object(api_client.session, 'post', return_value=mock_response)

    with allure.step('Send POST request with server error'):
        response = api_client.create_booking(booking_data)

    with allure.step('Check response status code'):
        assert response.status_code == 500, f"Expected status 500 but got {response.status_code}"


@allure.feature('Create booking')
@allure.story('Create booking with timeout')
def test_create_booking_timeout(api_client, mocker):
    booking_data = {
        "firstname": "",
        "lastname": "Doe",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2023-10-01",
            "checkout": "2023-10-05"
        },
        "additionalneeds": "Breakfast"
    }
    mocker.patch.object(api_client.session, 'post', side_effect=requests.Timeout)

    with allure.step('Send POST request with timeout'):
        with pytest.raises(requests.Timeout):
            api_client.create_booking(booking_data)





