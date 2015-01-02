"""
File: preprocess_data.py

Desc: This file takes the movie location data-file and preprocesses
it to find the lat/lon coordinates of the locations.
This consists of looking at the street addresses given and
using an online service to try and get a location for them.

Uses GeoPy:
https://geopy.readthedocs.org/en/1.6.0/#module-geopy.geocoders

"""

import copy
import csv
import re
import pickle
import geopy

Default_Location = (37.76526, -122.44388)

Raw_Movie_Data = 'data/film_locations_sf.csv'


def load_csv(filename):
    """
    Input: The filename for a CSV file.
    Ouput: Returns a list of all rows of the CSV file except the first one.
    This function reads a CSV file and returns the data rows as a list.
    Note: it assumes the first row is a list of titles and does not include this.
    """
    # reader = csv.reader(open(filename, newline=''), delimiter=',')
    file = open(filename, newline='')
    reader = csv.reader(file, delimiter=',')
    #
    # First row is column titles:
    row = next(reader)
    #
    data = []
    for row in reader:
        data.append(row)
    file.close()
    return data



def write_movie_keys(movie_keys, ofilename):
    """
    Input: a list of movie keys; and a filename
    Output: It writes the movie keys to the file.
    This function takes a list of movie names and writes it to a file
    formatted for including in the website as a Javascript variable.
    """
    file = open(ofilename, "w")
    file.write('<script>\n');
    file.write('   Movie_Keys = [\n');
    if len(movie_keys) > 0:
        for i in range(0, len(movie_keys)-1):
            file.write('            "{}",\n'.format(movie_keys[i]))
        file.write('            "{}"\n'.format(movie_keys[-1]))
    file.write('          ];\n');
    file.write('</script>\n');




def make_key(title, year):
    """
    Input: A movie title and year
    Ouput: The key for identifying this movie.
    Example: "A View to a Kill", 1985 => "A View to a Kill (1985)"
    Note: Year is added to title to handle reuse of movie names.
    """
    return title + ' (' + year + ')'


def create_movie_data(raw_data):
    """
    Input: A list of rows from the DataSF CSV file.
    Output: A structured data-structure for searching.
    Format:
      o Top layer is a dictionary on movie names
      o This contains a tuple consisting of:
        1. movie information: general info on this movie
        2. a list of movie locations
    """
    movies_db = dict()
    locations_db = dict()
    #
    for row in raw_data:
        movie_key = make_key(row[0].strip(), row[1])
        if not movie_key in movies_db:
            movie_data = {'title':row[0],
                          'year':row[1],
                          'prod_co':row[4],
                          'director':row[6],
                          'actor1':row[8],
                          'actor2':row[9],
                          'actor3':row[10]}
            # print('Adding movie: {}'.format(movie_key))
            movies_db[movie_key] = movie_data
            locations_db[movie_key] = []
        #
        loc_data = [row[2], row[3]]  # Format: [loc_desc, fun-fact]
        locations_db[movie_key].append(loc_data)
    #
    return movies_db, locations_db



def extract_loc_descs(loc_data):
    """
    Input: loc_data; A dictionary of {'movie-key', [List of location descriptions]}
    Output: A sorted list of parsed location descriptions.
    """
    loc_descs = []
    loc_keys = sorted(list(loc_data.keys()))
    for key in loc_keys:
        for loc in loc_data[key]:
            # print('extracting from: {}'.format(loc[0]))
            res = parse_location_base(loc[0])
            if type(res) == tuple:
                loc_descs.append(res[0])
                loc_descs.append(res[1])
            else:
                loc_descs.append(res)
    return sorted(list(set(loc_descs)))


def insert_latlng_data(loc_data, latlng_data):
    """
    Input:
    o loc_data: a dictionary of lists of location data, created from create_movie_data()
    o latlng_data: a dictionary mapping parsed location descriptions to lat-long values.
    Output:
    o the lat-long values are appended to the loc_data lists.
    """
    loc_keys = list(loc_data.keys())
    for key in loc_keys:
        for loc in loc_data[key]:
            res = parse_location_base(loc[0])
            if type(res) == tuple:
                latlng1 = latlng_data[res[0]]
                latlng2 = latlng_data[res[1]]
                loc.append([latlng1[0], latlng1[1], latlng2[0], latlng2[1]])
            else:
                latlng = latlng_data[res]
                loc.append([latlng[0], latlng[1]])
            



def sort_loc_by_lats(loc_data):
    """
    Input:
    o loc_data: a dictionary of lists of location data, created from create_movie_data()
    Output:
    o returns a list, sorted on lat values, of movie location info.
    """
    latlng_locs = []
    loc_keys = list(loc_data.keys())
    for key in loc_keys:
        for loc in loc_data[key]:
            latlngs = loc[-1]
            entry = [latlngs[0], latlngs, key, loc[0], loc[1]]
            latlng_locs.append(entry)
    latlng_locs.sort(key=lambda e: e[0])
    return latlng_locs
            


########################################################

# The following functions are for parsing a location description:

def clean_location(loc):
    """
    Input: a location description string that has been parsed.
    Output: this same string cleaned up in a couple of ways:
     - whitespace is trimmed
     - '&' is replaced by 'and'
     - text such as, 'near', "off of', is dropped
    """
    if not loc:
        return loc
    #
    loc = loc.strip()
    res = re.search('^and ([\w .&\']+)', loc, re.IGNORECASE)
    if res:
        loc = res.group(1)
    #
    res = re.search('^at ([\w .&\']+)', loc, re.IGNORECASE)
    if res:
        loc = res.group(1)
    #
    res = re.search('^near ([\w .&\']+)', loc, re.IGNORECASE)
    if res:
        loc = res.group(1)
    #
    res = re.search('^off of ([\w .&\']+)', loc, re.IGNORECASE)
    if res:
        loc = res.group(1)
    #
    res = re.search('^off ([\w .&\']+)', loc, re.IGNORECASE)
    if res:
        loc = res.group(1)
    #
    res = re.search('^Intersection of ([\w .&\']+)', loc, re.IGNORECASE)
    if res:
        loc = res.group(1)
    #
    res = re.search('^corner of ([\w .&\']+)', loc, re.IGNORECASE)
    if res:
        loc = res.group(1)
    #
    loc = loc.replace('&', 'and')
    return loc



def parse_simple_street(loc):
    """
    Input: A string containing a description of a location, eg '123 Pine St',
           after some preprocessing has been done to split out text enclosed
           in parentheses.
    Output:
      o The substring 'Pier[s]', followed by a number, if it is in the input string.
      o The substring consisting of a number followed by text but not containing commas
        (eg, '123 Central St') if it is in the input string.  Also, if the number is
        hyphenated (100-201 Broadway), then the first part of the number and hyphen
        are not included.
      o Otherwise returns None.
    """
    # print('parse_simple_street({})'.format(loc))
    # Handle Piers first:
    res = re.search('(Piers? [\d /]+)', loc)
    if res:
        return clean_location(res.group(0))
    # Next, search for '124 X St at Y St', we only want '124 X St':
    res = re.search('-*([\d]+) ([\da-zA-Z\ .\']+) at', loc)
    if not res:
        # Next, search for '124 X St':
        res = re.search('-*([\d]+) ([\da-zA-Z\ .\']+)', loc)
    if res:
        addr = res.group(1) + ' ' + res.group(2).strip()
        return clean_location(addr)
    #
    return clean_location(res)



def parse_intersection(loc):
    """
    Input: A string containing a description of a location, eg '123 Pine St'.
           This is after some preprocessing has been done to split out
           text enclosed in parentheses.
    Output:
      o If this string specifies an intersection of two streets, then
        return the substring that best specifies this.
        eg "Pine [at|&] Kearny" is an intersection.
      o returns None if no intersection is in the string description.
    Note: this does not handle descriptions which specify a range,
          such as "X from Y and Z"
    """
    res = re.search('([\da-zA-Z\ .\']+ & [\da-zA-Z\ .\']+)', loc)
    if res:
        return clean_location(res.group(0))
    #
    res = re.search('([\da-zA-Z\ .\']+ at [\da-zA-Z\ .\']+)', loc)
    if res:
        return clean_location(res.group(0))
    res = re.search('([\da-zA-Z\ .\']+ and [\da-zA-Z\ .\']+)', loc)
    if res:
        return clean_location(res.group(0))
    return res  # No success.



def parse_location(loc):
    """
    Input: A string containing a description of a location, eg '123 Pine St'.
           This is after some preprocessing has been done to split out
           text enclosed in parentheses.
    Output: A pair consisting of: 1. a parsed location; 2. a rating on how
            much information/accuracy is in this parsed location.
    """
    res = parse_simple_street(loc)
    if res:
        return (res, 1)
    res = parse_intersection(loc)
    if res:
        return (res, 2)
    # Assume something like landmark name or neighborhood so use entire
    # description, but assign a low accuracy/confidence score:
    return (loc, 100)



def split_on_parens(loc):
    """
    Input: A location description string.
    Output: It searches the string for a substring in which there is some
            text followed by more text in parentheses, eg 'aba daba (daba doo)'.
            and returns ['aba daba', 'daba doo'] in these cases.
            Otherwise it returns the entire string in a list: 'aba daba' => ['aba daba']
    Assumes that there is at most one set of ()s.
    """
    res = re.search('(.+)\((.+)\)', loc)
    if not res:
        # This location does not contain ()s, return None
        return [loc]
    #
    return [res.group(1).strip(), res.group(2).strip()]
    


def parse_location_single(loc):
    """
    This function parses a description string to identify a single-point
    location, as opposed to a location specified by two points.
    Input: A location description string.
    Ouput: A parsed string that best specifies the location.
    """
    if loc == '':
        return ''
    # print('parse_locations_single({})'.format(loc))
    addresses = []
    locs = split_on_parens(loc)
    for l in locs:
        res = parse_location(l)
        if res:
            addresses.append(res)
    best_loc = min(addresses, key = lambda t: t[1])
    return best_loc[0]




def parse_location_range(loc):
    """
    This function looks for and parses descriptions which specify a range.
    Examples of location ranges which are looked for:
      o X between Y and Z
      o X, between Y and Z
      o .*[,]X between Y and Z
      o X from Y and Z
      o X from Y & Z
      o X from Y to Z
    Input: A location description string.
    Output:
      o A pair or two location strings, if this is in the input,
          eg: ('X and Y', 'X and Z').
      o None, if a location range is not described.
    Note that in the SF-movie-locations dataset the X, Y and Z values tend to be
    very simple and need no further processing.
    """
    res = re.search('([\da-zA-Z\ .\']+),? between ([\da-zA-Z\ .\']+) and ([\da-zA-Z\ .\']+)', loc,
                    re.IGNORECASE)
    if not res:
        res = re.search('([\da-zA-Z\ .\']+),? between ([\da-zA-Z\ .\']+) & ([\da-zA-Z\ .\']+)', loc,
                        re.IGNORECASE)
    if not res:
        res = re.search('([\da-zA-Z\ .\']+) from ([\da-zA-Z\ .\']+) and ([\da-zA-Z\ .\']+)', loc,
                        re.IGNORECASE)
    if not res:
        res = re.search('([\da-zA-Z\ .\']+) from ([\da-zA-Z\ .\']+) & ([\da-zA-Z\ .\']+)', loc,
                        re.IGNORECASE)
    if not res:
        res = re.search('([\da-zA-Z\ .\']+) from ([\da-zA-Z\ .\']+) to ([\da-zA-Z\ .\']+)', loc,
                        re.IGNORECASE)
    if not res:
        res = re.search('([\da-zA-Z\ .\']+) at ([\da-zA-Z\ .\']+) and ([\da-zA-Z\ .\']+)', loc,
                        re.IGNORECASE)
    if not res:
        res = re.search('([\da-zA-Z\ .\']+) at ([\da-zA-Z\ .\']+) & ([\da-zA-Z\ .\']+)', loc,
                        re.IGNORECASE)
    #
    if not res:
        return res
    #
    loc1 = clean_location(res.group(1))
    loc2 = clean_location(res.group(2))
    loc3 = clean_location(res.group(3))
    #
    return ('{} and {}'.format(loc1, loc2),
            '{} and {}'.format(loc1, loc3))



def parse_location_base(loc):
    """
    Desc: Takes a raw location descriptions and returns a parsed location.
    Input: A raw location description, as read from the data source.
    Output: A parsed locations suitable for sending to a geocoder.
            This may be a single parsed-location (indicating a specific
            location), or a pair of parsed-locations (indicating a range).
    """
    # First test that loc contains text:
    if loc == '':
        return ''  # If no location text => return an empty string.
    # Next, check if loc parses to a street range:
    res = parse_location_range(loc)
    if res:
        return res
    # Default case, parse loc as a specific/single spot:
    return parse_location_single(loc)


def parse_locations(locations):
    """
    Desc: Takes a list of raw location descriptions and returns a list
          of parsed locations.
    Input: A list of location descriptions, as read from the data source.
    Output: A list of parsed locations suitable for sending to a geocoder.
            Each item may be a single parsed-location (indicating a specific
            location), or a pair of parsed-locations (indicating a range).
    """
    return [parse_location_base(loc) for loc in locations]



# End of functions for parsing a location description.

################################################################


def parse_locations_to_file(locations, dest_fname):
    """
    Desc: Takes a list of raw location descriptions, parses them, and writes the list to file.
    This was used in testing and development.
    """
    file = open(dest_fname, "w")
    for loc in locations:
        res = parse_location_base(loc)
        print('parse_locations() {} => {}'.format(loc, res))
        file.write('[{}] => [{}] (conf:{})\n'.format(loc, res[0], res[1]))
    file.close()



def write_list(l, fname):
    """
    Desc: Writes a list to a file, with each list-element on its own line.
    """
    file = open(fname, "w")
    for item in l:
        file.write('{}\n'.format(item))
    file.close()
    


def get_latlng(addr):
    """
    Desc: Gets the lag-lng values for a location string.
          It uses the GeoPy library and tries multiple geocoders to get a location.
          The first successful result is used.
    Input: A parsed location string.
    Output: A lat-lng pair.
    """
    if addr == '':
        return Default_Location
    addr = addr + ', San Francisco, CA'
    # geolocator = geopy.geocoders.Nominatim()
    # geolocators = [geopy.geocoders.OpenMapQuest(format_string='%s'), geopy.geocoders.Yandex(),
    #   geopy.geocoders.GoogleV3(), geopy.geocoders.GeocoderDotUS()]
    geolocators = [geopy.geocoders.GeocoderDotUS(), geopy.geocoders.GoogleV3()]
    for geoloc in geolocators:
        try:
            res = geoloc.geocode(addr)
            if res:
                return res[1]
        except Exception as e:
            print(e)
    return Default_Location


def get_latlngs(locs):
    """
    Desc: finds the lat-lng values for a list of parsed location/address strings
          using a geocoder.
    Input: A list of parsed addresses.
    Output: A dictionary mapping from address=>lat-lng values.
    """
    latlngs = {}
    for l in locs:
        res = get_latlng(l)
        latlngs[l] = res
    return latlngs



if __name__ == '__main__':
    print('SF Movies :: preprocessing data.')

    # 1. Read the CSV file containing movie data:
    raw_data = load_csv(Raw_Movie_Data)

    # 2. Convert the raw data into a dictionary of movie info and
    #    location info.
    movie_data, loc_data = create_movie_data(raw_data)

    # 3. Create the 'movie_keys.html' file, consisting of all movies with year (eg: 'Blah Blah (19XX)')
    # This file is used for the autocomplete feature in filtering on movie name.
    # format is:
    # <script>
    #   Movie_Keys = [
    #                   ...
    #                 ];
    # </script>
    movie_keys = sorted(list(movie_data.keys()))
    write_movie_keys(movie_keys, 'movie_keys.html')
    
    # 4. Create a database of unique locations and find their lat-lngs.
    loc_descs = extract_loc_descs(loc_data)

    # Uncomment the following two lines to find lat-lngs of the loc_descs:
    # loc_latlngs = get_latlngs(loc_descs)
    # pickle.dump(loc_latlngs, open( "latlon_data.p", "wb" ))
    loc_latlngs = pickle.load(open( "latlon_data.p", "rb" ))


    # 5. Insert these lat-lngs into loc_data:
    loc_data2 = copy.deepcopy(loc_data)
    insert_latlng_data(loc_data2, loc_latlngs)

    # 6. Create a list of locations sorted on lat:
    lat_data = sort_loc_by_lats(loc_data2)


    # 7. Write these processed data structures to file.
    #    These files will be used by the website as the database.
    pickle.dump(movie_data, open( "movie_data.p", "wb" ))
    pickle.dump(loc_data2, open( "loc_data.p", "wb" ))
    pickle.dump(lat_data, open( "lat_data.p", "wb" ))
