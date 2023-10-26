import connect
import requests
import threading
import tinydb

def create_backup():
    db = connect.db_link
    users = tinydb.TinyDB("data/users_ids.json")
    #Удаляем предыдущий бэкап
    requests.put(f"{db}/users.json", json={})
    for i in users.table("users"):
        requests.patch(f"{db}/users.json", json=i)

    irreg_quest = tinydb.TinyDB("data/irregular_questions.json")
    requests.put(f"{db}/quests.json", json={})
    for i in irreg_quest.table("questions"):
        requests.patch(f"{db}/backup.json", json=i)

    t = threading.Timer(20, create_backup)