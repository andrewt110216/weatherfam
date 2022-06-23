// Add Person Page - Google Maps Plugin to Pick Location

// Get latitude, longitude from HTML, if available
var lat = document.getElementById('lat').value
var lng = document.getElementById('long').value

// Initialize locationPicker plugin
var lp = new locationPicker('map', {
    lat: parseFloat(lat),
    lng: parseFloat(lng),
    zoom: 50 // defaults to 15
});

// Listen to map idle event, listening to idle event more accurate than listening to ondrag event
google.maps.event.addListener(lp.map, 'idle', function (event) {
// Get current location and show it in HTML
var location = lp.getMarkerPosition();
    document.getElementById('lat').value = location.lat;
    document.getElementById('long').value = location.lng;
});