"""
File: movie_db_test.py
Desc: Unit tests for movie_db.py
"""

import unittest
import movie_db as mdb


class MovieDbTest(unittest.TestCase):
    def test_get_movie_info(self):
        # Test on an empty key:
        res = mdb.get_movie_info('')
        self.assertEqual(res, [])

        # Test on a movie-key in the DB:
        res = mdb.get_movie_info('About a Boy (2014)')
        self.assertEqual(res, {'title': 'About a Boy',
                               'director': 'Mark J. Kunerth',
                               'actor1': 'David Walton',
                               'prod_co': 'NBC Studios',
                               'year': '2014', 'actor3': '',
                               'actor2': 'Minnie Driver'})

        # Test on a movie-key not in the DB:
        res = mdb.get_movie_info("Ocean's 11 (2001)")
        self.assertEqual(res, [])


    def test_get_locs_by_key(self):
        # Test on an empty key:
        res = mdb.get_locs_by_key('')
        self.assertEqual(res, [])

       # Test on a movie-key not in the DB:
        res = mdb.get_locs_by_key("Ocean's 11 (2001)")
        self.assertEqual(res, [])

        # Test on a movie-key in the DB:
        res = mdb.get_locs_by_key('About a Boy (2014)')
        self.assertEqual(res,
                         [['Crissy Field', '', [37.8039069, -122.4640618]],
                          ['Powell from Bush and Sutter', '',
                           [37.790228, -122.408582, 37.789328, -122.408482]],
                          ['Broderick from Fulton to McAlister',
                           '', [37.776729, -122.439682, 37.7775871, -122.4400305]]])


    def test_get_locs_by_indexes(self):
        # Test on an empty locs:
        res = mdb.get_locs_by_indexes([])
        self.assertEqual(res, [])

        # Test on valid indexes:
        res = mdb.get_locs_by_indexes([5, 18, 25])
        self.assertEqual(res,
                         [["Guess Who's Coming to Dinner (1967)",
                           'San Francisco International Airport',
                           'SFO has a museum dedicated to aviation history. ',
                           [37.6213129, -122.3789554]],
                          ['The Princess Diaries (2001)',
                           'Firestation #3 (Brazil Avenue and Athens Street)', '',
                           [37.721431, -122.428382]],
                          ['Blue Jasmine (2013)', '330 Santa Clara Ave.', '',
                           [37.734211, -122.465729]]])


        # Test on invalid index:
        res = mdb.get_locs_by_indexes([5000])
        self.assertEqual(res, [])

        # Test mix of valid and invalid indexes:
        res = mdb.get_locs_by_indexes([5000, 15, -100, 877])
        self.assertEqual(len(res), 2)
                         

    def test_get_indexes_by_loc(self):
        # Test on empty info:
        res = mdb.get_indexes_by_loc(0, 0, 0)
        self.assertEqual(res, [])

        # Test on a valid input that gets at least one 'point' location:
        res = mdb.get_indexes_by_loc(37.7787, -122.5127, 1000.0)
        self.assertEqual(res, [391, 392, 393, 457, 458, 459])

        # Test on a valid input that gets at least one 'range' location:
        res = mdb.get_indexes_by_loc(37.78373, -122.46329, 500.0)
        self.assertEqual(res, [484, 485])

        # Test on a valid input that has no locations in radius:
        res = mdb.get_indexes_by_loc(34.78373, -128.46329, 500.0)
        self.assertEqual(res, [])


    def test_calc_great_circle_dist(self):
        # Test pairs of points and verify that the distance is within 1% of expected.
        # Note: small differences can be due to different choices in radius of Earth.
        #       large differences are most likely a bug.
        test_pairs = [([37.7763, -122.4346, 37.8005, -122.4159], 10344.5),
                      ([32.9697, -96.80322, 29.46786, -98.53506], 1387005)]
        for input, output in test_pairs:
            d = mdb.calc_great_circle_dist(input[0], input[1], input[2], input[3])
            # print('{} =? {}'.format(d, output))
            self.assertTrue(abs(d - output) < output/100.0)


    def test_find_lat_range_ft(self):
        # Test various input sets of [lat, lng, radius]
        # Verify that the min latitude range is about [lat,lng]-radius
        # and that the max latitude range is about [lat,lng]+radius.
        test_vals = [[37.7763, -122.0, 1000.0],
                     [35.0, 120.0, 3180.0]]
        for input in test_vals:
            min_lat, max_lat = mdb.find_lat_range_ft(input[0], input[2])
            self.assertTrue(min_lat < input[0])
            self.assertTrue(max_lat > input[0])

            # Test distance from (lat,lng) to (min_lat, lng) and verify that it is
            # within 1% of radius.
            d = mdb.calc_great_circle_dist(input[0], input[1], min_lat, input[1])
            self.assertTrue(abs(d - input[2]) < input[2]/100.0)

            # Test distance from (lat,lng) to (max_lat, lng) and verify that it is
            # within 1% of radius.
            d = mdb.calc_great_circle_dist(input[0], input[1], min_lat, input[1])
            self.assertTrue(abs(d - input[2]) < input[2]/100.0)



if __name__ == '__main__':
    unittest.main()

