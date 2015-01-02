# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, json
from contextlib import closing
import movie_db as mdb


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
## Instead of 'app.config.from_object(), can use the following
## to configure from a file:
# app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# Index/Home/Splash page for this website:
@app.route('/')
def index():
    if app.debug:
        print("index - requested")
    return render_template('index.html')


# Given a movie key ('Movie Name (Year)'),
# Returns info on that movie.
# Note: this is not currently being used.
@app.route('/get_movie_info', methods=['GET'])
def get_movie_info():
    response = jsonify(movie_key='', info=[])  # Response on error
    try:
        key = request.args.get('movie_key')
        if app.debug:
            print('get_movie_info({})'.format(key))
        if not key:
            # Not a valid query, return error-response:
            return response
        movie_info = mdb.get_movie_info(key)
        response = jsonify(movie_key=key, info=movie_info)
    except:
        pass
    return response



# Given a movie key ('Movie Name (Year)'),
# Returns location information for that movie key.
@app.route('/get_by_key', methods=['GET'])
def get_by_key():
    response = jsonify(movie_key='', locs=[])  # Response on error
    try:
        key = request.args.get('movie_key')
        if app.debug:
            print('get_by_key(' + key + ') - started')
        if not key:
            # Not a valid query, return error-response:
            return response
        movie_locs = mdb.get_locs_by_key(key)
        response = jsonify(movie_key=key, locs=movie_locs)
    except:
        pass
    return response



# Given a list of indexes into the latitute-sorted data file.
# Returns the movie locations at those indexes.
@app.route('/get_by_indexes', methods=['GET'])
def get_by_indexes():
    response = jsonify(locs=[])  # Response on error
    try:
        indexes_str = json.loads(request.args.get('indexes'))
        if not indexes_str:
            # Not a valid query, return error-response:
            return response
        indexes = []
        for val in indexes_str:
            indexes.append(int(val))
        if app.debug:
            print('get_by_indexes() - indexes: {}'.format(indexes))
        movie_locs = mdb.get_locs_by_indexes(indexes)
        response = jsonify(locs=movie_locs)
    except:
        pass
    return response



# Given a lat-lng and radius,
# Returns the indexes into the latitude-sorted data file.
@app.route('/get_indexes_by_loc', methods=['GET'])
def get_indexes_by_loc():
    # Response on error
    if app.debug:
        print('get_indexes_by_loc() - started')
    response = jsonify(lat=0, lng=0, radius=0, indexes=[])
    try:
        rad = request.args.get('radius')
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        if (not rad) or (not lat) or (not lng):
            # Not a valid query, return error-response:
            return response
        rad = float(rad)
        lat = float(lat)
        lng = float(lng)
        if app.debug:
            print('get_indexes_by_loc({},{},{})'.format(lat,lng,rad))
        movie_indexes = mdb.get_indexes_by_loc(lat, lng, rad)
        response = jsonify(lat=lat, lng=lng, radius=rad,
                           indexes=movie_indexes)
    except:
        pass
    return response



if __name__ == '__main__':
    app.debug = True
    if app.debug:
        print("sfmovies - starting ..")
    app.run()


