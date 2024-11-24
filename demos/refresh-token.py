from scolengo_api import Skolengo
import json
import time
import os


def on_refresh_token():
    token = {
        "tokenSet": user.tokenSet,
        "school": user.school
    }

    file_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(file_path, "token.json"), 'w+') as f:
        json.dump(token, f, indent=2)

        print("Refreshed token has been written to json file.")


with open("token.json", "r+", encoding='utf-8') as f:
    config = json.load(f)

print("Token valid until:", time.ctime(config["tokenSet"]["expires_at"]))

with Skolengo.fromConfigObject(config) as user:
    user.config['onTokenRefresh'] = on_refresh_token

    user_info = user.getUserInfo()
    print(f"Correctement authentifié sous l'identifiant {user_info['id']}")
    print(f"Session de {user_info['firstName']} {user_info['lastName']}")

    user.refreshToken()