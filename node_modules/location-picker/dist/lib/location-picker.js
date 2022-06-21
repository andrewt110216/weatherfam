"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("./location-picker.css");
var LocationPicker = /** @class */ (function () {
    function LocationPicker(element, options, mapOptions) {
        if (options === void 0) { options = {}; }
        if (mapOptions === void 0) { mapOptions = {}; }
        var pO = {
            setCurrentPosition: true
        };
        Object.assign(pO, options);
        var mO = {
            center: new google.maps.LatLng(pO.lat ? pO.lat : 34.4346, pO.lng ? pO.lng : 35.8362),
            zoom: 15
        };
        Object.assign(mO, mapOptions);
        // Allow both, a string with the element's id or a direct reference to the element
        if (element instanceof HTMLElement) {
            this.element = element;
        }
        else {
            this.element = document.getElementById(element);
        }
        this.map = new google.maps.Map(this.element, mO);
        // Append CSS centered marker element
        var node = document.createElement('div');
        node.classList.add('centerMarker');
        if (this.element) {
            this.element.classList.add('location-picker');
            this.element.children[0].appendChild(node);
        }
        // Set center to current position if attribute `setCurrentPosition` is true and no initial position is set
        if (pO.setCurrentPosition && !pO.lat && !pO.lng) {
            this.setCurrentPosition();
        }
    }
    LocationPicker.prototype.getMarkerPosition = function () {
        var latLng = this.map.getCenter();
        return { lat: latLng.lat(), lng: latLng.lng() };
    };
    LocationPicker.prototype.setLocation = function (lat, lng) {
        this.map.setCenter(new google.maps.LatLng(lat, lng));
    };
    LocationPicker.prototype.setCurrentPosition = function () {
        var _this = this;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var pos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                _this.map.setCenter(pos);
            }, function () {
                console.log('Could not determine your location...');
            });
        }
        else {
            console.log('Your browser does not support Geolocation.');
        }
    };
    return LocationPicker;
}());
exports.default = LocationPicker;
//# sourceMappingURL=location-picker.js.map