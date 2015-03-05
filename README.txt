SF Movies
====================
http://sfmovies15.herokuapp.com/


by: Greg Hornby

https://github.com/ghornby
www.linkedin.com/pub/greg-hornby
http://scholar.google.com/citations?user=6aX2s1YAAAAJ&hl=en&oi=ao

CONTENTS:

1. Overview / Description
2. Approach / Solution
3. API
4. Future Work
5. References


========================================================

1. Overview / Description

This project consists of source code and data files for implementing
a website which shows on a map where movies have been filmed in the
city of San Francisco.  It was a one week project I developed to
learn Flask and to have a demo-able website to show to others.

What this website does is it allows users to find filming locations
for movies which had scenes filmed in San Francisco.  The interface
allows the user to filter for filming locations in two ways:
o The user can type in a movie title, which has autocomplete,
  and then all locations for that movie will be shown on the map.
o The user can position a red marker on the map, specify a
  radius, and then request all filming locations in that region.

In addition, clicking the 'About' button produces a modal
that gives a simple description of the website.


========================================================

2. APPROACH / SOLUTION

To create this website I wanted to write the backend in Python.
Going from there, I decided to use Flask as the web framework
since it is Python based and I had the impression that it was
well suited to doing small projects such as this.  For context,
a few years ago I had developed a website using PHP on the backend,
and then in 2014 I did some work (primarily front-end) on a Django
website.

On the front-end, I had used Javascript/jQuery and Twitter Bootstrap
on my two previous websites so I decided to stick with those rather
than trying to learn a new front-end framework.

For hosting, I wanted to use Heroku since I had some experience
with that with my prior Django project and that seemed to work
well and be relatively easy to use.

Data was taken from DataSF and downloaded as CSV file to
analyze/preprocess offline.

As for a database, I had used MySQL with my PHP website, but it
seems that the database to use for Flask is Postgres.  Also,
Postgres seems to be preferred database on Heroku.  Unfortunately,
a quick look at online resources suggested that it might take
some time to learn how to get going with Postgres with Flask
and Heroku.  Fortunately, the project did not seem to require
much of a database (just reading data, no storing) so I could
get by with just reading from files.

Users needed to be able to search by movie title, and for this there
needed to be an autocomplete on this field -- which makes sense since
its hard to know which films used SF for filming locations.  In
addition, I wanted users to be able to select a location and
search/filter for filming locations near that location.
I wanted to show this to the user using a map and markers
on the map.  Looking over the data I saw that some location
descriptions showed that the location was over some stretch,
sometimes covering several blocks, and I wanted to be able to
show that on the map.  Of the three main online map systems
Leaflet seemed to be the one that was easiest to learn as well
as allowing the developer to draw a range of shapes.


One of the first considerations was how to index movies.  Since
there are a few movies which have the same name I chose to use
a string combining title and year, (eg "Ocean's 11 (2001)") so
as to have a unique key.


The pseudo-database for searching for movies would use the tables:
o movie_data: a dictionary mapping from movie-key to all the non-location
  movie information (eg producer, actors, etc) for that movie.
o loc_data: a dictionary mapping from movie-key to a list of all
  filming locations for that movie.
This was readily done by reading the CSV file line by line and
adding the info to the two dictionaries.  These dictionaries were
saved to file using pickle.


To put markers on the map at the appropriate location required
taking the location description provided in the data and
converting that to latitude and longitude coordinates.
Various online geocoding services exist and there are various
Python libraries for using multiple ones.  I wanted to be able
to use more than one service (for redundancy and reliability)
and I tried a few of these and settled on GeoPy as making it
easy to try a variety of different geocoding sites easily.
From testing, I found that geocoder.us and Google did the best
job so I settled on those.

Since geocoding services tend to only allow a limited number
of free queries a day, I needed to be a bit efficient in my
use of querying them.  I noticed that there is some duplication
of addresses, so I decided to sort out all the unique locations
and create a dictionary of lat-lngs for them.  These values
would be stored to file for reuse even as I did development
on other parts of this project.

Location descriptions in the data were written for humans,
and so these text strings required parsing to put them in
a form that was good for the geocoders to understand.
These descriptions tended to fall in a couple of categories:
o A landmark, eg 'Randall Musuem'.  Sometimes this is mispelled.
o A street address: 555 Market St.
o A street address with extra info: Jawbone at 99 Rhode Island St.
o A pier: Pier 33; or Pier 43 1/2
o An intersection: Mason & California Streets
o One or more blocks: Powell from Bush and Sutter
o Content added in parentheses: Epic Roasthouse (399 Embarcadero)
  - Sometimes the more useful information was outside the parentheses,
    sometimes it was inside the parentheses.

Parsing use the following algorithm:
o Test a block of text to find if it specifies multiple blocks,
  eg 'X between Y and Z'.
  Since locations that used multiple blocks were in a fairly standard
  format ('X from Y to Z') with just a few variations on whether it
  was from/between/down and to/and/&/, this was checked for first
  using regular expressions to grab out the X, Y and Z values.
  If the string matches one of these patterns, then return a location
  pair specifying this as follows: ((X and Y), (X and Z)).

If the description is not of multiple blocks then it must be a
single-point address.  
o Look for parentheses, and split out the text inside and outside.
  Parse each substring separately, with a score/confidence assigned to
  each parsing and then pick the coordinates associated with the highest
  scoring block to use.
o For each block, look for:
  - A numbered street address:  123 Broadway St
  - A pier: Pier 39
  - An intersection: X & Y; X at Y; X and Y; etc.
  - If none of these patterns match, then assume the block of text
    specifies a landmark, but give this parsing a low confidence score.

    
Once all location descriptions had been parsed, they were sorted and duplicates
were removed and then this list of locations was sent to the geocoding
services to get the lat-lng values.  A dictionary mapping from description
to lat-lngs was then saved to file.  In addition, these values were then
inserted into the datastructure containing the mapping from movie-keys to
a list of its filming locations.


The front-end consists of a fairly straight-forward index based
on the simple Bootstrap of example of a navbar with content in
the main div.  I put an 'About' button and configured that with
a Bootstrap modal to have a way to provide info on the website,
the data, and the developer (me).

I used a jQuery UI autocomplete field to give an autocomplete
functionality when searching on movies.  To provide data for
this, I wrote a Python function to extract movie titles and
years from the DataSF CSV file, and write them to file as the
values in a Javascript list.  This list would then be included
by the index.html template to populate the autocomplete field.


jQuery is used to catch button-click events and trigger the appropriate
handlers to process search/filter on movie name or find movies
in a given radius about a location.  For finding movies by
movie name and year, this sends a GET request to the server
to get all filming locations associated with that movie.
Since movies do not have many film locations, all of these
values are returned in the response to the initial request.

Handling get filming location within a given radius of a location
is more interesting.  First, when the server gets the request,
it searches the locations dataset by loading up a datafile of
filming locations sorted by latitude.  It then calculates the
minimum and maximum latitude ranges of the search-circle and
uses these as the limits for a search through the datafile.
There it uses a great-circle distance calculation to see if
the filming location falls in the radius.
One concern is that there can be hundreds of movies within a
given radius and this may overflow the maximum message size
of a response.  To address this, the request for movie locations
within a given radius requests indexes for the locations, then
asks for the data for the indices in blocks of up to 10 values.
For example:
o client requests all filming locations 2000 ft from a given location
o server responds with 27 indexes.
o the client then sends the server requests for the locations
  for indexes 0-9 in one GET request, then indexes 10-19 in a
  second GET request, then indexes 20-27 in a third request.
o the server gets these three requests and sends the data back
  to the client.
o the client then takes this data to put markers on the map.


========================================================

3. API

This section documents the API for interfacing to the backend.


/get_movie_info
o Input: {movie_key}
o Output: {movie_key, info}

This GET request is to get all the non-location information on a movie
associated with the given movie_key.  This key is in the format
  'Movie Title (Year)'; eg. "Ocean's 11 (2001)".
The response is in JSON format and consists of the given movie key
along with a dictionary of information about it:
  {'prod_co', 'actor1', 'year', 'actor2', 'director', 'actor3' 'title'}



/get_by_key
o Input: {movie_key}
o Output: {movie_key, locs}

This GET request returns all location information for the given movie_key.
The response data is in JSON format and is a dictionary with the movie
key, 'movie_key' and locations, 'locs'.

Here 'locs' is a list in which each entry is either the list
['location description', 'fun fact', [lat1, lng1]].  or the list
['location description', 'fun fact', [lat1, lng1, lat2, lng2]].  The
first case is for when the filming happened at a single location, the
second case is for when the filming took place over a stretch of area.



/get_by_indexes
o Input: {indexes}
o Output: {locs}

This GET request takes as input a JSON'ed list of indexes into the locations
data file.  It returns a JSON'ed list, in which for each valid index in
indexes, there is an entry in the output list, 'locs'.

Here 'locs' is a list in which each entry is either the list
['location description', 'fun fact', [lat1, lng1]].  or the list
['location description', 'fun fact', [lat1, lng1, lat2, lng2]].  The
first case is for when the filming happened at a single location, the
second case is for when the filming took place over a stretch of area.



/get_indexes_by_loc
o Input: {lat, lng, radius}
o Output: {lat, lng, radius, indexes}

This GET request takes as input a latitude, longitude and radius
and it returns these values along with a JSON'ed list of indexes.
This list of indexes consists of indexes for a locations in the
locations data file that occurred within the specified radius
of the specified coordinates.



========================================================

4. FUTURE WORK

The existing system works pretty well and I really like the result.
Some things I'm thinking of adding are:

o Clean up the frontend UI.
  - eg Restrict map to only show SF area.
  - Once searched for, put info on a movie on the page.
  - Possibly link to something like IMDB to get additional info.

o Currently if there is more than one marker at a given coordinate,
  only the top one is visible.  Find a way to show all markers.

o A couple of unit tests need to be added.  Also, the unit tests should
  be less hard-coded to the existing data and be more adaptive to updates
  in them.

o Improve the parsing of location descriptions.  Existing failures
  - 'Broadway (North Beach)'  => The geocoder picks a point somewhere on Broadway
    that isn't in North Beach.
  - 'Market Street (from 6th- 4th Streets)' => existing code process what's inside
    the parentheses separate from the text outside.
  - 'Golden Gate Park' => This is a large area and not a point.
  - '0-100 block Halleck Street' => this is a block and not a point.

o /get_by_indexes currently returns data for all indexes in its input and
  this can result in overflowing the maximum response size.  To address this,
  it should max out on the number of locations it returns.
  For example, by only returning data for the first N indexes in its input.

o One of the next things I want to get familiarity with is learning to
  use a database with Flask so I'd like to extend this system to use that.
  Here I'd likely use either Postgres or MySQL.


========================================================

5. REFERENCES

Here are links to external resources I used:

o GeoPy
 - https://geopy.readthedocs.org/en/1.6.0/#module-geopy.geocoders

o Leaflet:  http://leafletjs.com/

Data on which movies have been filmed in SF is from:
o DataSF: Film Locations: 
https://data.sfgov.org/Culture-and-Recreation/Film-Locations-in-San-Francisco/yitu-d5am?


