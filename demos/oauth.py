from scolengo_api import Skolengo, REDIRECT_URI
from playwright.sync_api import sync_playwright
import json
import os


def auth_browser(auth_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(auth_url)

        # Wait for the callback URL to be detected in a network event
        callback = page.wait_for_event("request", lambda response: REDIRECT_URI in response.url)

        browser.close()

        return callback.url
    

def authenticate_user(school_name):

    # Retrieve matching schools to school_name from skolengo api
    schools = Skolengo.searchSchool(school_name)
    selected_school = schools[0]
    print(selected_school)
    
    # Initialize oid client
    oid_client, config = Skolengo.getOIDClient(selected_school)

    # Get url to sign in page
    auth_url, state = oid_client.create_authorization_url(config['authorization_endpoint'])
    print(auth_url)

    # Retrieve url with authorization code by signing in
    callback_url = auth_browser(auth_url)
    print(callback_url)

    # Exchange the authorization code for tokens
    token_set = oid_client.fetch_token(config['token_endpoint'],
                                       authorization_response=callback_url,
                                       client_secret=oid_client.client_secret)

    token = {
        "tokenSet": token_set,
        "school": selected_school
    }
    return token


token = authenticate_user("Lycée International Victor Hugo")
print(token)

file_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(file_path, "token.json"), 'w+') as f:
    json.dump(token, f, indent=2)

print("Wrote to json file.")