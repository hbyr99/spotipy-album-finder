# Import dependencies
import requests
import spotipy
import json

# Insert your API ID and Secret key here
CLIENT_ID = ''
CLIENT_SECRET = ''


# POST
auth_response = requests.post('https://accounts.spotify.com/api/token', {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

# Track ID from the URI
track_id = '6y0igZArWVi6Iz0rj35c1Y'

# actual GET request with proper header
r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)

# Request user for artist ID
print("Welcome to album finder!")
print("Insert the artist ID: ")
artist_id = input()

# GET request for albums
albums = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
                      headers=headers,
                      params={'include_groups': 'album', 'limit': 10})
album_list = albums.json()

for album in album_list['items']:
    print(album['name'], ' --- ', album['release_date'])
