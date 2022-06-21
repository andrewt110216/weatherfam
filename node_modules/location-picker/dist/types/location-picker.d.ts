/// <reference types="googlemaps" />
import MapOptions = google.maps.MapOptions;
import Map = google.maps.Map;
import './location-picker.css';
export default class LocationPicker {
    element: HTMLElement | null;
    map: Map;
    constructor(element: string | HTMLElement, options?: LocationPickerOptions, mapOptions?: MapOptions);
    getMarkerPosition(): {
        lat: number;
        lng: number;
    };
    setLocation(lat: number, lng: number): void;
    setCurrentPosition(): void;
}
export interface LocationPickerOptions {
    setCurrentPosition?: boolean;
    lat?: number;
    lng?: number;
}
