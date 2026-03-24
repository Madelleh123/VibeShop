import requests

try:
    response = requests.get("http://127.0.0.1:8000/")
    response.raise_for_status()  # Raise an exception for bad status codes
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
