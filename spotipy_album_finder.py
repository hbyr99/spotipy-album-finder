# Import dependencies
from sqlalchemy import create_engine
import requests
import spotipy
import json
import os
import pandas as pd
import matplotlib.pyplot as plt


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
    col_names = ['artist', 'album', 'release_date']
    albums_df = pd.DataFrame(columns=col_names)

    # Insert the data into the dataframe
    for album in album_list['items']:
        albums_df.loc[len(albums_df.index)] = [
            album['artists'][0]['name'],
            album['name'],
            album['release_date']
        ]

    return albums_df


# User Command Line Interface

def menu():
    # Start main program loop
    print("Welcome to album finder!")

    while True:
        option = input(
            """
What would you like to do?
(1) -- Read new albums from Spotify
(2) -- Show albums details stored
(3) -- Open album information from file
(4) -- Save album information to file
(5) -- Visualize data
(0) -- Quit
Enter choice: """
        )

        if option == '0':
            print("Goodbye!")
            break

        elif option == '1':
            # Fetch albums
            album_list = album_get().json()

            while True:
                options = input("""
Albums fetched!
Choose action to take:
(1) -- Show albums fetched (returns here after execution)
(2) -- Store albums information
(3) -- Discard albums information
Enter choice: """)

                if options == '1':
                    print_albums(album_list)

                elif options == '2':
                    database_menu(data_to_df(album_list))
                    break

                elif options == '3':
                    break

                else:
                    print("Invalid input!")

        elif option == '2':
            albums_stored = pd.read_sql_table(
              'albums',
              con=create_engine('mysql://root:codio@localhost/album_finder')
            )
            print(albums_stored)

        elif option == '3':
            file_name = input("Enter file name to load album information: ")

            table_name = 'album_finder'
            os.system(
              'mysql -u root -pcodio -e "CREATE DATABASE IF NOT EXISTS '
              + album_finder + '; "'
            )
            os.system("mysql -u root -pcodio album_finder < " + file_name)

        elif option == '4':
            file_name = input("Enter file name to store album information: ")
            os.system("mysqldump -u root -pcodio album_finder > " + file_name)

        elif option == '5':
            albums_stored = pd.read_sql_table(
                        'albums',
                        con=create_engine(
                          'mysql://root:codio@localhost/album_finder'))
            while True:
                action = input("""
Choose action:
(1) -- Bar Chart
(2) -- Mean number of albums
(3) -- Median number of albums

Enter choice: """)
                if action == '1':
                    barplot(albums_stored, 'artist')
                    break

                elif action == '2':
                    dataframe_mean(albums_stored, 'artist')
                    break

                elif action == '3':
                    dataframe_median(albums_stored, 'artist')
                    break

                else:
                    print("Invalid input!")
        else:
            print("Invalid input!")


# Print album names with release date

def print_albums(album_list):
    for album in album_list['items']:
        print(album['artists'][0]['name'],
              ' --- ',
              album['name'],
              ' --- ',
              album['release_date'])


# Select data insertion mechanism
def database_menu(albums_df):
    # Create databse if non existent
    os.system(
      'mysql -u root -pcodio -e "CREATE DATABASE IF NOT EXISTS album_finder; "'
    )

    while True:
        option = input(
          "Append(0) or overwrite(1) the album data onto the database? "
        )
        if option == '0':
            database_append(albums_df)
            break
        elif option == '1':
            database_overwrite(albums_df)
            break
        else:
            print("Invalid input! ")


# Overwrite data in Database
# Test 1: Engine is created --- TO DO!
# Test 4: Albums data is inserted into the database --- TO DO!

def database_overwrite(albums_df):
    engine = create_engine(
      'mysql://root:codio@localhost/album_finder')
    albums_df.to_sql('albums',
                     con=engine,
                     if_exists='replace',
                     index=False)


# Append data to Database
# Test 1: Engine is created --- TO DO!
# Test 4: Albums data is appended into the database --- TO DO!

def database_append(albums_df):
    engine = create_engine(
      'mysql://root:codio@localhost/album_finder')
    albums_df.to_sql('albums',
                     con=engine,
                     if_exists='append',
                     index=False)


# Draw bar graph of artist and albums stored

def barplot(dataframe, column_name):
    df = pd.DataFrame(
      dataframe.pivot_table(index=[column_name],
                            aggfunc='size'))
    fig, ax = plt.subplots()
    position = 2
    for artist, albums in df.iterrows():
        ax.bar(x=artist,
               height=albums,
               width=0.8,
               label=artist)
        ++position

    ax.set_xlabel(column_name)
    ax.set_title('Number of ' + column_name)
    plt.show()


def dataframe_mean(dataframe, column_name):
    df = pd.DataFrame(
      dataframe.pivot_table(index=[column_name],
                            aggfunc='size'))
    print(df.iloc[0].mean())


def dataframe_median(dataframe, column_name):
    df = pd.DataFrame(
      dataframe.pivot_table(index=[column_name],
                            aggfunc='size'))
    print(df.iloc[0].median())


# Main code
if __name__ == '__main__':
    menu()
