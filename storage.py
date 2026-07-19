import json
import os

DATA_DIR = "user_data"

def _get_user_file(email):
    os.makedirs(DATA_DIR, exist_ok=True)
    safe_email = email.replace("@", "_at_").replace(".", "_")
    return os.path.join(DATA_DIR, f"{safe_email}.json")

def load_chats(email):
    file_path = _get_user_file(email)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {"Chat 1": []}  # default for a brand new user

def save_chats(email, chats):
    file_path = _get_user_file(email)
    with open(file_path, "w") as f:
        json.dump(chats, f)