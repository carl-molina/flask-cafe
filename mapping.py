import os
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.environ['MAPQUEST_API_KEY']
print('This is API_KEY', API_KEY)

def get_map_url(address, city, state):
    """Crafts MapQuest URL for a static map for this location."""

    base = f"https://www.mapquestapi.com/staticmap/v5/map?key={API_KEY}"
    print('This is base URL w/ MAPQUEST_API_KEY', base)

    where = f"{address},{city},{state}"
    # ^ How MapQuest API wants their locations to be handled. Will work even w/
    # spaces in address. Spaces become '%20'.

    print('URL structured to Mapquest API request,'
          f"{base}&center={where}&size=@2x&zoom=15&locations={where}"
    )
    return f"{base}&center={where}&size=@2x&zoom=15&locations={where}"


def save_map(id, address, city, state):
    """Gets static map and saves as jpg file in '/static/maps' directory of
    this app.
    """

    path = os.path.abspath(os.path.dirname(__file__))
    # ^ this gets you the absolute path to whichever directory this file is
    # located.
    print('This is path', path)

    map_url = get_map_url(address, city, state)
    print('This is map_url', map_url)

    resp = requests.get(map_url)
    # ^ Sends an HTTP GET request to map_url (MapQuest Static Map API resource)
    print('This is resp', resp)
    print('This is resp.content', resp.content)
    # ^ resp.content is the binary content of resp, which should be an img)

    with open(f"{path}/static/maps/{id}.jpg", "wb") as file:
        file.write(resp.content)