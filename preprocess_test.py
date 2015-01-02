"""
File: preprocess_test.py
Desc: Unit tests for preprocess_data.py
"""


import unittest
import preprocess_data as ppd


class PreprocessTest(unittest.TestCase):
    def test_load_csv(self):
        # Test on a short, test file:
        data = ppd.load_csv('data/test_data.csv')
        self.assertEqual(len(data), 5)
        self.assertEqual(len(data[0]), 3)
        self.assertEqual(data[0][0], 'GAVIOTA WAY')
        self.assertEqual(data[0][1], 'GAVIOTA')
        self.assertEqual(data[0][2], 'WAY')
        self.assertEqual(len(data[-1]), 3)
        self.assertEqual(data[-1][0], 'GENE FRIEND WAY')
        self.assertEqual(data[-1][1], 'GENE FRIEND')
        self.assertEqual(data[-1][2], 'WAY')

        data2 = ppd.load_csv(ppd.Raw_Movie_Data)
        self.assertEqual(len(data2[0]), 11)
        self.assertEqual(data2[0][0], '180')
        self.assertEqual(data2[0][1], '2011')
        self.assertEqual(data2[0][2], 'Randall Musuem')


    def test_write_movie_keys(self):
        # Can try a couple of test cases and verify the resulting file
        # is in the correct format.
        # print('test_write_movie_keys() - TBI')
        return True

    def test_make_key(self):
        # Test on a couple of inputs:
        self.assertEqual(ppd.make_key('A Movie', '2012'), 'A Movie (2012)')
        self.assertEqual(ppd.make_key('Yet Another Movie', '1921'), 'Yet Another Movie (1921)')


    def test_create_movie_data(self):
        raw_data = ppd.load_csv(ppd.Raw_Movie_Data)
        movie_data, loc_data = ppd.create_movie_data(raw_data)

        # Test that a couple of entries were created correctly
        # in the movies_data data structure:
        test_pairs_movies = [('Babies (2010)',
                             {'actor3': 'Mari', 'actor2': 'Hattie', 'director': 'Thomas Balmes',
                              'title': 'Babies', 'year': '2010', 'prod_co': 'Canal+',
                              'actor1': 'Bayar'}),
                             ('Hemingway & Gelhorn (2011)',
                              {'actor3': 'Tom Cruise', 'actor2': 'Clive Owen',
                               'director': 'Philip Kaufman', 'title': 'Hemingway & Gelhorn',
                               'year': '2011',
                               'prod_co': 'Attaboy Films, For Whom Productions, Home Box Office (HBO)',
                               'actor1': 'Nicole Kidman'})]
        for input, output in test_pairs_movies:
            self.assertEqual(movie_data[input], output)


        # Test that a couple of entries were created correctly
        # in the loc_data data structure:
        test_pairs_locs = [('Hemingway & Gelhorn (2011)',
                            [['Muni Metro East (501 Cesar Chavez)', '']]),
                           ('Dream with the Fishes (1997)',
                            [['Bay Bridge', 'Before opening in 1936, the bridge was blessed by Cardinal Secretary of State Eugene Cardinal Pacelli, who later became Pope Pius XII. '],
                             ['Pier 39', '']])]
        for input, output in test_pairs_locs:
            self.assertEqual(loc_data[input], output)


    def test_extract_loc_descs(self):
        # print('test_extract_locs_descs() - TBI')
        return True
       
    def test_insert_latlng_data(self):
        # print('test_sort_latlng_data() - TBI')
        return True
       
    def test_sort_loc_by_lats(self):
        # print('test_sort_loc_by_lats() - TBI')
        return True


    def test_clean_location(self):
        locs_pairs = [('Market & 2nd Streets', 'Market and 2nd Streets'),
                      ('Intersection of California at Polk', 'California at Polk'),
                      ('Intersection of York & Peralta', 'York and Peralta'),
                      ('off of Taylor Street and Filbert', 'Taylor Street and Filbert'),
                      ('950 Mason Street', '950 Mason Street'),
                      ('near Potrero and Cesar Chavez Streets', 'Potrero and Cesar Chavez Streets'),
                      ('at 820 Mission', '820 Mission'),
                      ('Near Point Lobos', 'Point Lobos'),
                      ("O'Farrell Street at Powell", "O'Farrell Street at Powell")]
        for input, output in locs_pairs:
            self.assertEqual(ppd.clean_location(input), output)


    def test_parse_simple_street(self):
        self.assertEqual(ppd.parse_simple_street('Crissy Field'), None)
        self.assertEqual(ppd.parse_simple_street('Leavenworth from Filbert & Francisco St'), None)
        self.assertEqual(ppd.parse_simple_street('Pine between Kearney and Davis'), None)
        self.assertEqual(ppd.parse_simple_street('2 Montgomery Street'), '2 Montgomery Street')
        self.assertEqual(ppd.parse_simple_street('950 Mason Street, Nob Hill'), '950 Mason Street')
        self.assertEqual(ppd.parse_simple_street('Vallejo St. Garage, 766 Vallejo St.'), '766 Vallejo St.')
        self.assertEqual(ppd.parse_simple_street('303-305 S. Van Ness'), '305 S. Van Ness')

    def test_parse_intersection(self):
        locs_pairs = [('Corner of Van Ness & Mission Street', 'Van Ness and Mission Street'),
                      ('901 Mission Street', None),
                      ('950 Mason Street, Nob Hill', None),
                      ('Montgomery & Market Streets', 'Montgomery and Market Streets'),
                      ('Filbert Street at Hyde', 'Filbert Street at Hyde'),
                      ('1298 Sacramento Street at Jones', '1298 Sacramento Street at Jones'),
                      ('Sutter & Buchannan Streets', 'Sutter and Buchannan Streets'),
                      ('24th and Church St. ', '24th and Church St.'),
                      ('Café Trieste', None),
                      ('The Café at 2369 Market St.', None),
                      ('Pier 7', None)]
        for input, output in locs_pairs:
            self.assertEqual(ppd.parse_intersection(input), output)


    def test_parse_location(self):
        locs_pairs = [("Starbucks at 333 O'Farrell St.", ("333 O'Farrell St.", 1)),
                      ("2000 Folsom", ("2000 Folsom", 1)),
                      ("2413 Harrison St.", ("2413 Harrison St.", 1)),
                      ("Muddy Waters Coffee House", ("Muddy Waters Coffee House", 100)),
                      ("24th and Church St. ", ("24th and Church St.", 2))]
        for input, output in locs_pairs:
            self.assertEqual(ppd.parse_location(input), output)


    def test_parse_location_single(self):
        test_pairs = [('Corner of Van Ness & Mission Street', 'Van Ness and Mission Street'),
                      ("24th and Church St. ", "24th and Church St."),
                      ('Intersection of California at Polk', 'California at Polk'),
                      ('near Potrero and Cesar Chavez Streets', 'Potrero and Cesar Chavez Streets'),
                      ('Montgomery & Market Streets', 'Montgomery and Market Streets'),
                      ('Café Trieste', 'Café Trieste'),
                      ('The Café at 2369 Market St.', '2369 Market St.'),
                      ("21st St & Sanchez", "21st St and Sanchez"),
                      ("Mark Hopkins Intercontinental Hotel (1 Nob Hill Circle, Nob Hill)",
                       "1 Nob Hill Circle"),
                      ("McDonald's Restaurant (701 3rd Street, SOMA)",
                       "701 3rd Street"),
                      ("Broadway Studios (435 Broadway at Montgomery Street)",
                       "435 Broadway"),
                      ("23rd & Iowa Streets (Dogpatch)", "23rd and Iowa Streets"),
                      ('', '')]
        for input, output in test_pairs:
            self.assertEqual(ppd.parse_location_single(input), output)


    def test_parse_location_range(self):
        test_pairs = [('Corner of Van Ness & Mission Street', None),
                      ("Nam Yuen Restaurant (740 Washington Street, Chinatown)", None),
                      ("Folsom & Essex Streets", None),
                      ("Off Bush Street, between Powell and Stockton Streets",
                       ("Bush Street and Powell", "Bush Street and Stockton Streets")),
                      ("Howard St. from Embarcadero to 11 St.",
                       ("Howard St. and Embarcadero", "Howard St. and 11 St.")),
                      ("Leavenworth from Filbert & Francisco St",
                       ("Leavenworth and Filbert", "Leavenworth and Francisco St")),
                      ("420 Jones St. at Ellis St.", None),
                      ("(916 Grant Avenue at Washington, Chinatown", None),
                      ("Lombard at Hyde", None),
                      ("Columbus Avenue at Green & Stockton",
                       ("Columbus Avenue and Green", "Columbus Avenue and Stockton")),
                      ("Mission at 1st and 2nd",
                       ("Mission and 1st", "Mission and 2nd")),
                      ("", None)]
        for input, output in test_pairs:
            self.assertEqual(ppd.parse_location_range(input), output)

    def test_parse_location_base(self):
        test_pairs = [('Corner of Van Ness & Mission Street', 'Van Ness and Mission Street'),
                      ("Columbus Avenue at Green & Stockton",
                       ("Columbus Avenue and Green", "Columbus Avenue and Stockton")),
                      ("Off Bush Street, between Powell and Stockton Streets",
                       ("Bush Street and Powell", "Bush Street and Stockton Streets")),
                      ('Café Trieste', 'Café Trieste'),
                      ("21st St & Sanchez", "21st St and Sanchez"),
                      ('Corner of Van Ness & Mission Street', 'Van Ness and Mission Street'),
                      ("", "")]
        for input, output in test_pairs:
            self.assertEqual(ppd.parse_location_base(input), output)

        
    def test_get_latlng(self):
        # print('test_get_latlng() - TBI')
        # Note: geocoders have a fixed number of free requests/day
        return True

        


if __name__ == '__main__':
    unittest.main()

