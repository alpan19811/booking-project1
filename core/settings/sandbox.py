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