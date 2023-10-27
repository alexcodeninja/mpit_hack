import tinydb
from tinydb import Query
users = tinydb.TinyDB("data/users_ids.json")
qur = Query()
print(users.table("users").search(qur.id == 123))
