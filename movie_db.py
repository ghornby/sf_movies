"""
File: movie_db.py

This file is the interface to the SF movie data, which comes from
the DataSF website:
  https://data.sfgov.org/Culture-and-Recreation/Film-Locations-in-San-Francisco/yitu-d5am

This data has been downloaded and preprocessed (see ./preprocessed)
and is pickled and stored into different data files in ./static.
"""

import bisect
import pickle
from math import degrees, radians, cos, sin, asin, sqrt


Movie_Data_Filename = 'data/movie_data.p'
Loc_Data_Filename = 'data/loc_data.p'
Lat_Data_Filename = 'data/lat_data.p'

Earth_Radius_Ft = 20925524.9  # Radius of the Earth in feet.



def get_movie_info(movie_key):
    """
    Input: a movie key
    Output: the dictionary entry associated with that key from the
            movie data file.
    """
    try:
        file = open(Movie_Data_Filename, "rb" )
        movie_data = pickle.load(file)
        file.close()
        if not movie_key in movie_data:
            return []
        return movie_data[movie_key]
    except:
        print('get_move_info() - failed')
        pass
    return []  # Return empty list if things fail.


def get_locs_by_key(movie_key):
    """
    Input: a movie key
    Output: the dictionary entry associated with that key from the
            locations data file.
    """
    try:
        file = open(Loc_Data_Filename, "rb" )
        loc_data = pickle.load(file)
        file.close()
        if not movie_key in loc_data:
            return []
        return loc_data[movie_key]
    except:
        pass
    return []  # Return empty list of things fail.




def get_locs_by_indexes(indexes):
    """
    Input: a list of indexes into lat_data to retrieve.
    Output: A list in of entries containing this location data.
    """
    loc_results = []
    try:
        file = open(Lat_Data_Filename, "rb" )
        lat_data = pickle.load(file)
        file.close()
        for i in indexes:
            if (i < 0) or (i >= len(lat_data)):
                # Invalid index, skip this.
                continue
            loc_entry = [lat_data[i][2], lat_data[i][3], lat_data[i][4], lat_data[i][1]]
            loc_results.append(loc_entry)
    except:
        pass
    return loc_results



def get_indexes_by_loc(lat, lng, radius):
    """
    Input: latitude, longitude and a radius.
    Output: Indexes into lat_data of all movie locations that fall within the
            given radius of that location.
    """
    # print('get_indexes_by_loc({},{},{})'.format(lat,lng,radius))
    loc_results = []
    try:
        file = open(Lat_Data_Filename, "rb" )
        lat_data = pickle.load(file)
        file.close()
        #
        # The extra 250ft is to pick a range to handle finding line-segments:
        min_lat, max_lat = find_lat_range_ft(lat, radius+250)
        #
        keys = [l[0] for l in lat_data]
        i_start = bisect.bisect_left(keys, min_lat)
        i_stop = bisect.bisect_left(keys, max_lat)
        # print('lat range:: {}:{}, ({},{})'.format(min_lat, max_lat, i_start, i_stop))
        #
        for i in range(i_start, i_stop):
            # For both points and line segments, the first two values in lat_data[1]
            # are lat-lng values, so check if this is in the radius:
            if calc_great_circle_dist(lat, lng, lat_data[i][1][0], lat_data[i][1][1]) <= radius:
                loc_results.append(i)
                continue  # Once added, no need to check if this is a line segment.
            #
            if len(lat_data[i][1]) == 4:
                # This handles the line segment case, in which the 4 entries are
                # two pairs of lat-lngs.
                if calc_great_circle_dist(lat, lng, lat_data[i][1][2], lat_data[i][1][3]) <= radius:
                    loc_results.append(i)
    except Exception as e:
        print('error:{}'.format(e))
        pass
    #
    return loc_results




def calc_great_circle_dist(lat1, lon1, lat2, lon2, radius=Earth_Radius_Ft):
    """
    Desc: computes and returns the Great Circle distance between two points.
    Input: lat/lng values using decimal degrees.
    """
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    #
    d=2*asin(sqrt((sin((lat1-lat2)/2))**2 + 
                  cos(lat1)*cos(lat2)*(sin((lon1-lon2)/2))**2))
    #
    return d*radius



def find_lat_range_ft(lat, radius):
    """
    Input: a latitude and a radius (in feet).
    Output: a pair specifying the minimum and maximum latitudes for
            which are within that radius.
    Note: This probably does not handle latitudes near the poles.
    """
    delta = degrees(radius / Earth_Radius_Ft)
    return lat-delta, lat+delta


