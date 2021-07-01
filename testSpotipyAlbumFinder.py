# Import dependencies
import unittest
import json
import pandas as pd
from os import path
from unittest.mock import patch
from spotipy_album_finder import (
                                  fetch_keys,
                                  auth_response,
                                  album_get,
                                  data_to_df)


class TestSpotipyAlbumFinder(unittest.TestCase):
    def test_fetch_keys(self):
        self.assertTrue(path.exists('config.txt'))
        keys = fetch_keys()
        self.assertTrue(type(keys) is tuple)
        self.assertNotEqual(keys[0], '')
        self.assertNotEqual(keys[1], '')

        with open('config.txt', 'r') as source:
            self.assertEqual(keys[0], source.readline().strip())
            self.assertEqual(keys[1], source.readline().strip())

    def test_auth_response(self):
        keys = fetch_keys()
        response = auth_response(keys[0], keys[1])
        self.assertNotEqual(response, None)
        self.assertEqual(response.status_code, 200)
        try:
            response.json()
        except ValueError:
            raise ValueError('Conversion to JSON failed.')

    @patch('spotipy_album_finder.input', create=True)
    def test_album_get(self, mocked_input):
        mocked_input.side_effect = ['2wUjUUtkb5lvLKcGKsKqsR', 20]
        albums = album_get()
        self.assertNotEqual(albums, None)
        try:
            albums.json()
        except ValueError:
            raise ValueError('Conversion to JSON failed.')

    @patch('spotipy_album_finder.input', create=True)
    def test_data_to_df(self, mocked_input):
        mocked_input.side_effect = ['2wUjUUtkb5lvLKcGKsKqsR', 20]
        albums_df = data_to_df(album_get().json())
        self.assertTrue(isinstance(albums_df, pd.DataFrame))
        self.assertNotEqual(len(albums_df), 0)


if __name__ == '__main__':
    unittest.main()
