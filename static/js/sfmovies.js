/*
The Javascript source for the SF Movies website.
*/


var Map;                   // Leaflet map object.
var Movie_Locs_Layer;      // Layers to store markers for Leaflet maps.
var Loc_Marker;            // Marker to specify a location to search around.
var Default_Location = [37.76526, -122.44388];




function clear_map()
{
    // This function clears all markers from the Movie_Locs_Layer.
    // Since all markers (except the red Loc_Marker) are on this layer,
    //  this effectively clears the entire map (except for the red Loc_Marker).

    // console.log("clear_map()");
    Movie_Locs_Layer.clearLayers();
}

function add_loc_marker(movie_key, latlng, desc, funfact)
{
    // This function adds a movie marker to the Movie_Locs_Layer,
    //   which results in the marker being added to the map.

    if (latlng.length < 2) {
	// If latlng entry is not an array of 2 values, use the Default_Location:
	latlng = Default_Location;
    }
    //	console.log(" - " + locs[i]);

    var marker = null;
    if (latlng.length == 2) {
	// Handle location of: A single point:
	marker = L.marker(latlng);
    } else {
	// Handle location of: A line segment:
	console.log(" - Line segment?:" + latlng);
	marker = L.polyline([[latlng[0], latlng[1]],
			     [latlng[2], latlng[3]]],
			    { color: 'blue', weight: 20});
    }

    if (marker != null) {
	// Construct the location message/info and bind to the marker:
	msg = "<p><b>" + movie_key + "</b><br>" + desc + "</p>";
	if (funfact != "") {
	    msg += "<p>" + funfact + "</p>";
	}
	marker.bindPopup(msg);
	Movie_Locs_Layer.addLayer(marker); // Add to the map layer.
    }
}



function handle_get_by_key_response(msg)
{
    // This function is called when the user clicks the
    // button, '#but-filter-name', to get all locations
    // associated with a given movie.

    /*
      Location data is stored in msg.locs and is formated as follows:
      locs[i]: location entries
      locs[i][0]: location description
      locs[i][1]: location fun facts
      locs[i][2]: lat-longs:  lat:locs[i][2][0]; long:locs[i][2][1]
    */
    // console.log("handle_get_by_key_response() - started");
    movie_key = msg.movie_key;
    locs = msg.locs;

    clear_map();
    for (var i=0; i<locs.length; i++) {
	desc = locs[i][0];
	funfact = locs[i][1];
	latlng = locs[i][2];
	add_loc_marker(movie_key, latlng, desc, funfact);
    }
}

function handle_get_by_key(event)
{
    // This function is called when the user clicks the button, '#but-filter-name',
    // to get all locations associated with a given movie.
    // It sends a GET request to the server to get this information.

    movie_key = $('#movieName').val();
    $.get(Get_by_Key_URL,
	  {'movie_key': movie_key},
	  handle_get_by_key_response);
}



function handle_index_loc_resp(msg)
{
    // This function is called when the client receives the message from
    // the server containing location info.
    // This function loops through the locations in the message and
    // calls the function to add a marker on the map for each one.
    locs = msg.locs;
    for (var i=0; i<locs.length; i++) {
	movie_key = locs[i][0];
	desc = locs[i][1];
	funfact = locs[i][2];
	latlng = locs[i][3];
	add_loc_marker(movie_key, latlng, desc, funfact);
    }
}


function handle_get_indexes_resp(msg)
{
    // This function is called when the client receives a response message from the
    // server with a list of indexes into the database of filming locations.
    // It then requests info for these locations from the server so they
    // can be added to the map.

    // Clear the map and add a red circle showing the filter/search radius:
    clear_map();
    lat = msg.lat;
    lng = msg.lng;
    radius = msg.radius;
    indexes = msg.indexes;
    rad_meters = radius * 0.3048; // Convert feet to meters, units for Leaflet.
    circle = L.circle([lat, lng], rad_meters, {color:'red'});
    Movie_Locs_Layer.addLayer(circle);

    // For each filming location in this search radius (represented by an index),
    // this loops and does a GET request to the server to get the appropriate
    // location information.  It groups indexes in blocks of up to 10.
    for (var i=0; i<indexes.length; i += 10) {
	vals = indexes.slice(i, Math.min(i+10, indexes.length));
	vals_str = JSON.stringify(vals)
	$.get(Get_by_Indexes_URL,
	  {'indexes': vals_str},
	  handle_index_loc_resp);
    }
}


function handle_get_by_loc(event)
{
    // This function is called when the user clicks on the get-by-location button:
    // '#but-filter-loc'
    // It sends a GET request to the server to get all filming locations within
    // the specified radius of the Loc_Marker's coordinates.

    radius = $('#radius').val();

    latlng = Loc_Marker.getLatLng();
    console.log('handle_get_by_loc()' + radius + latlng.lat);

    $.get(Get_Indexes_by_Loc_URL,
	  {'lat': latlng.lat, 'lng': latlng.lng, 'radius': radius},
	  handle_get_indexes_resp);
}


function handle_map_click(latlng)
{
    // This function is called when the user clicks or double-clicks on
    // the map is then re-positions Loc_Marker to that location.

//    console.log("map-click:" + latlng + '; ' + typeof(latlng))
    Loc_Marker.setLatLng(latlng)
}


function map_setup()
{
    // This function setups up the map, which uses the Leaflet library:
    //    http://leafletjs.com/

    init_loc = Default_Location;
    Map = L.map('map').setView(init_loc, 12);
    
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(Map);


    Movie_Locs_Layer = new L.LayerGroup();
    Movie_Locs_Layer.addTo(Map);

    // Create the Loc_Marker, which is the red marker to indicate the center
    // of a location-radius for searching/filtering by location:
    red_icon =  L.icon({
	iconUrl: Static_URL + 'images/marker-icon-red.png',
	shadowUrl: Static_URL + 'images/marker-shadow.png',
	iconSize:     [25, 41], // size of the icon
	shadowSize:   [41, 41], // size of the shadow
	iconAnchor:   [12, 40], // point of the icon which will correspond to marker's location
	popupAnchor:  [0, -25] // point from which the popup should open relative to the iconAnchor
	//	shadowAnchor: [4, 62],  // the same for the shadow
    });

    Loc_Marker = L.marker(init_loc, {icon: red_icon});
    Loc_Marker.bindPopup('Click on the map to move this red marker, then use filter-by-location to find movie locations nearby.');
    Loc_Marker.addTo(Map);


    // Setup response functions to re-position the Loc_Marker when the map is
    // clicked and double-clicked.  Note: double-clicking is also used for this since
    // single-clicks don't get caught on mobile devices.
    // Also, disable zoom on double-click since
    // this action is being used to position the Loc_Marker.
    Map.on('click', function(e) {
	handle_map_click(e.latlng);
    });
    Map.on('dblclick', function(e) {
	handle_map_click(e.latlng);
    });
    Map.doubleClickZoom.disable(); 
}



$(window).load(function()
{
    // Attach responses to the two buttons to filter filming locations:
    $('#but-filter-name').click(handle_get_by_key);
    $('#but-filter-loc').click(handle_get_by_loc);

    // Setup the map:
    map_setup();

    // Configure the autocomplete field:
    $( "#movieName" ).autocomplete({
	source: Movie_Keys
    });
});

