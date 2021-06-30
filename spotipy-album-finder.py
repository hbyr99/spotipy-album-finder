# Import dependencies
import requests
import spotipy
import json
import pandas as pd
from sqlalchemy import create_engine

# base URL of all Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1/'

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

# Request user for artist ID and number of albums to pull
print("Welcome to album finder!")
print("Insert the artist ID: ")
artist_id = input()

print("How many albums would you like to see? ")
limit = int(input())

# GET request for albums
albums = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
                      headers=headers,
                      params={'include_groups': 'album', 'limit': limit})
album_list = albums.json()

for album in album_list['items']:
    print(album['name'], ' --- ', album['release_date'])

# creating data frame to add data to
col_names = ['album', 'release_date']
albums_df = pd.DataFrame(columns=col_names)
for album in album_list['items']:
    albums_df.loc[len(albums_df.index)] = [
        album['name'], album['release_date']
    ]

print('I got this far!')
print(albums_df)

engine = create_engine('mysql://root:codio@localhost/album_finder')
albums_df.to_sql('albums', con=engine, if_exists='replace', index=False)
