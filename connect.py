# This file is wrap for requests
# and needs to simplify working with the database
import requests

db_url = ""

def patch_data(url_data=str, **data):
    requests.patch(url=db_url+url_data+"/.json", json=data)

def post_data(url_data=str, **data):
    requests.post(url=db_url+url_data+"/.json", json=data)

def delete_data(url_data=str, **data):
    requests.delete(url=db_url+url_data+"/.json", json=data)

def put_data(url_data=str, **data):
    requests.put(url=db_url+url_data+"/.json", json=data)

def get_data(url_to_data=str):  # Получает данные пользователя из users по логину
    return requests.get(f"{db_url}/{url_to_data}/.json").json()

def is_connected():
    try:
        return requests.get("https://amn-project-b3b8c-default-rtdb.europe-west1.firebasedatabase.app").ok
    except requests.ConnectionError:
        return False