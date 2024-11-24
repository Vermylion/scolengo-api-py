from scolengo_api import Skolengo
import json
import time

with open("token.json", "r+", encoding='utf-8') as f:
    config = json.load(f)

print("Token valid until:", time.ctime(config["tokenSet"]["expires_at"]))

with Skolengo.fromConfigObject(config) as user:

    user_info = user.getUserInfo()
    print(f"Correctement authentifié sous l'identifiant {user_info['id']}")
    print(f"Session de {user_info['firstName']} {user_info['lastName']}")

    info = user.getAgenda('2024-11-25', '2024-11-26')
    
    pretty_info = json.dumps(info, indent=2)
    print(pretty_info)