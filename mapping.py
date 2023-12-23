import os
import requests

API_KEY = os.environ.get("MAPQUEST_API_KEY")

def get_map_url(address, city, state):
    """Get MapQuest URL for a static map for this location."""

    base = f"https://www.mapquestapi.com/staticmap/v5/map?key={API_KEY}"
    where = f"{address},{city},{state}"
    return f"{base}&center={where}&size=@2x&zoom=15&locations={where}"


def save_map(id, address, city, state):
    """Get static map and save in static/maps directory of this app."""

    path = os.path.abspath(os.path.dirname(__file__))
    # ^ this gets you the absolute path to wherever this file is located.
    print('This is path', path)

    # FIXME: get URL for map, download it, and save ith with a path like
    # "PATH/static/maps/1.jpg"

    map_url = get_map_url(address, city, state)

    resp = requests.get(map_url)
    print('This is resp', resp)
    print('This is resp.content', resp.content)

    with open()


    # TODO: left off here for the night! Tomorrow:
    # 1. Figure out a way to get Mapquest API jpg download working
    # 2. Figure out a way to save Mapquest API jpg to /static/maps directory
    # 3. Figure out a way to pin an icon to the specific location.
    # 4. Read the documentation!