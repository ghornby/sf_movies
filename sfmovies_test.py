"""
File: sfmovies_test.py
Desc: Unit tests for sfmovies.py
"""


import os
import sfmovies
import unittest
import tempfile
from flask import json, jsonify


class SFMoviesTestCase(unittest.TestCase):
    def setUp(self):
        # No DB setup required.
        self.app = sfmovies.app.test_client()

    def tearDown(self):
        # No DB teardown required.
        return True

    def test_get_movie_info(self):
        # Test on an empty key:
        key1 = ''
        msg = dict(movie_key=key1)
        rv = self.app.get('/get_movie_info', query_string=msg)
        data1 = json.loads(rv.data)
        self.assertEqual(data1['movie_key'], key1)
        self.assertEqual(len(data1['info']), 0)

        # Test for an invalid input:
        key2 = 'blah blah'
        msg = dict(bad_arg=key2)
        rv = self.app.get('/get_movie_info', query_string=msg)
        data2 = json.loads(rv.data)
        self.assertEqual(data2['movie_key'], '')
        self.assertEqual(len(data2['info']), 0)
        
        # Test on a movie-key in the DB:
        key = 'About a Boy (2014)'
        msg = dict(movie_key=key)
        rv = self.app.get('/get_movie_info', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['movie_key'], key)
        self.assertEqual(data['info'],
                         {'title': 'About a Boy',
                          'director': 'Mark J. Kunerth',
                          'actor1': 'David Walton',
                          'prod_co': 'NBC Studios',
                          'year': '2014', 'actor3': '',
                          'actor2': 'Minnie Driver'})
        
        # Test on a movie-key not in the DB:
        key = "Ocean's 11 (2001)"
        msg = dict(movie_key=key)
        rv = self.app.get('/get_movie_info', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['movie_key'], key)
        self.assertEqual(data['info'], [])


    def test_get_by_key(self):
        # Test on an empty key:
        key = ''
        msg = dict(movie_key=key)
        rv = self.app.get('/get_by_key', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['movie_key'], key)
        self.assertEqual(len(data['locs']), 0)

        # Test for invalid inputs:
        key = 'blah blah'
        msg = dict(bad_arg=key)
        rv = self.app.get('/get_by_key', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['movie_key'], '')
        self.assertEqual(len(data['locs']), 0)
        
        # Test on a movie-key in the DB:
        key = 'About a Boy (2014)'
        msg = dict(movie_key=key)
        rv = self.app.get('/get_by_key', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['movie_key'], key)
        self.assertEqual(data['locs'],
                         [['Crissy Field', '', [37.8039069, -122.4640618]],
                          ['Powell from Bush and Sutter', '',
                           [37.790228, -122.408582, 37.789328, -122.408482]],
                          ['Broderick from Fulton to McAlister',
                           '', [37.776729, -122.439682, 37.7775871, -122.4400305]]])

        # Test on a movie-key not in the DB:
        key = "Ocean's 11 (2001)"
        msg = dict(movie_key=key)
        rv = self.app.get('/get_by_key', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['movie_key'], key)
        self.assertEqual(data['locs'], [])



    def test_by_indexes(self):
        ## Note that this test is only valid for a particular lat_data file
        ##   and these values are hard-coded to that file.
        ## Should load that file here and verify the returned output against that.

        # Test on an empty input:
        msg = dict(locs='')
        rv = self.app.get('/get_by_indexes', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(len(data['locs']), 0)

        # Test for invalid get args:        
        msg = dict(bad_arg='blah blah')
        rv = self.app.get('/get_by_indexes', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(len(data['locs']), 0)

        # Test on valid indexes:
        msg = dict(indexes=json.dumps([5, 18, 25]))
        rv = self.app.get('/get_by_indexes', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data,
                         {'locs': [["Guess Who's Coming to Dinner (1967)",
                                    'San Francisco International Airport',
                                    'SFO has a museum dedicated to aviation history. ',
                                    [37.6213129, -122.3789554]],
                                   ['The Princess Diaries (2001)',
                                    'Firestation #3 (Brazil Avenue and Athens Street)', '',
                                    [37.721431, -122.428382]],
                                   ['Blue Jasmine (2013)', '330 Santa Clara Ave.', '',
                                    [37.734211, -122.465729]]]})


        # Test on invalid index:
        msg = dict(indexes=json.dumps([5000]))
        rv = self.app.get('/get_by_indexes', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(len(data['locs']), 0)


        # Test mix of valid and invalid indexes:
        msg = dict(indexes=json.dumps([5000, 15, -100, 877]))  # Only 15 and 877 are valid.
        rv = self.app.get('/get_by_indexes', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(len(data['locs']), 2)



    def test_get_indexes_by_loc(self):
        # Test on empty info:
        msg = dict(radius='0', lat='0', lng='0')
        rv = self.app.get('/get_indexes_by_loc', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['lat'], 0)
        self.assertEqual(data['lng'], 0)
        self.assertEqual(data['radius'], 0)
        self.assertEqual(data['indexes'], [])

        # Test on invalid arg values:
        msg = dict(radius='not', lat='valid', lng='values')
        rv = self.app.get('/get_indexes_by_loc', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['lat'], 0)
        self.assertEqual(data['lng'], 0)
        self.assertEqual(data['radius'], 0)
        self.assertEqual(data['indexes'], [])


        # Test on incorrect get args:
        msg = dict(wrongArg='blah blah')
        rv = self.app.get('/get_indexes_by_loc', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['lat'], 0)
        self.assertEqual(data['lng'], 0)
        self.assertEqual(data['radius'], 0)
        self.assertEqual(data['indexes'], [])


        # Test on a valid input that gets at least one 'point' location:
        msg = dict(radius='1000.0', lat='37.7787', lng='-122.5127')
        rv = self.app.get('/get_indexes_by_loc', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['lat'], 37.7787)
        self.assertEqual(data['lng'], -122.5127)
        self.assertEqual(data['radius'], 1000.0)
        self.assertEqual(data['indexes'], [391, 392, 393, 457, 458, 459])

        # Test on a valid input that gets at least one 'range' location:
        msg = dict(radius='500.0', lat='37.78373', lng='-122.46329')
        rv = self.app.get('/get_indexes_by_loc', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['lat'], 37.78373)
        self.assertEqual(data['lng'], -122.46329)
        self.assertEqual(data['radius'], 500.0)
        self.assertEqual(data['indexes'], [484, 485])

        # Test on a valid input that has no location in radius:
        msg = dict(radius='10.0', lat='34.7787', lng='-128.5127')
        rv = self.app.get('/get_indexes_by_loc', query_string=msg)
        data = json.loads(rv.data)
        self.assertEqual(data['lat'], 34.7787)
        self.assertEqual(data['lng'], -128.5127)
        self.assertEqual(data['radius'], 10.0)
        self.assertEqual(data['indexes'], [])



if __name__ == '__main__':
    unittest.main()

