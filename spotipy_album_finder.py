# Import dependencies
from sqlalchemy import create_engine
import requests
import spotipy
import json
import pandas as pd

# Retrieve API ID and Secret key from config.txt
# Test 1: config.txt exists
# Test 2: Client ID is not empty
# Test 3: Client Secret is not empty
# Test 4: Client ID is first string in config
# Test 5: Client Secret is second string in config

def fetch_keys():
    with open('config.txt', 'r') as config:
        client_id = config.readline().strip()
        client_secret = config.readline().strip()

    return (client_id, client_secret)


# POST
# Test 1: Response is not empty
# Test 2: Response has status code 200
# Test 3: Return value is in json format

def auth_response(identifier, secret):
    response = requests.post('https://accounts.spotify.com/api/token', {
        'grant_type': 'client_credentials',
        'client_id': identifier,
        'client_secret': secret,
    })
    # Return the response
    return response


# GET request for albums
# Test 1: Albums is not empty
# Test 2: Return value is in json format
# Test 3: Artist ID is valid
# Test 4: Limit is an unsigned integer between 1 and 50

def album_get():
    # Base URL of all Spotify API endpoints
    BASE_URL = 'https://api.spotify.com/v1/'
    
    # Fetch key for API
    keys = fetch_keys()
    
    # Request Artist ID and album limit from user
    artist_id = input("Insert the artist ID: ")
    limit = int(input("How many albums would you like to see? "))
    
    # Save the access token
    auth_response_data = auth_response(keys[0], keys[1]).json()
    access_token = auth_response_data['access_token']

    # Send GET request
    headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}
    albums = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
                          headers=headers,
                          params={'include_groups': 'album', 'limit': limit})

    return albums


# Convert data format to DataFrame
# Test 1: albums_df is a DataFrame
# Test 2: albums_df is not empty

def data_to_df(album_list):
    # Create a dataframe to place the data into
    col_names = ['album', 'release_date']
    albums_df = pd.DataFrame(columns=col_names)

    # Insert the data into the dataframe
    for album in album_list['items']:
        albums_df.loc[len(albums_df.index)] = [
            album['name'], album['release_date']
        ]

    return albums_df

# User Command Line Interface
# Test 1: Album list is not empty

def menu():
    # Request user for artist ID and number of albums to pull
    print("Welcome to album finder!")

    # Print album names with release date
    album_list = album_get().json()
    for album in album_list['items']:
        print(album['name'], ' --- ', album['release_date'])

    # Insert album details into DataBase
    df_to_db(data_to_df(album_list))



# Insert data into DataBase
# Test 1: Engine is created
# Test 2: Database exists
# Test 3: Albums DataFrame is not empty
# Test 4: Albums data is insert into the database

def df_to_db(albums_df):
    engine = create_engine('mysql://root:codio@localhost/album_finder')
    albums_df.to_sql('albums', con=engine, if_exists='replace', index=False)


# Main code
if __name__ == '__main__':
    menu()
