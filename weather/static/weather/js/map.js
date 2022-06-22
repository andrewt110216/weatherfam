// Add Person Page - Google Maps Plugin to Pick Location

// Initialize locationPicker plugin
var lp = new locationPicker('map', {
setCurrentPosition: true, // You can omit this, defaults to true
}, {
zoom: 15 // You can set any google map options here, zoom defaults to 15
});

// Listen to map idle event, listening to idle event more accurate than listening to ondrag event
google.maps.event.addListener(lp.map, 'idle', function (event) {
// Get current location and show it in HTML
var location = lp.getMarkerPosition();
document.getElementById('lat').value = location.lat;
document.getElementById('long').value = location.lng;
});