# WeatherFam
*A weather app focused on people instead of zip codes*

## Introduction

A web app that allows you to track the weather for every member of your "WeatherFam" &ndash; your friends and family living anywhere in the world.

On your home page, you can see the current and forecasted weather for all members of your WeatherFam in one place! No more scrolling through pages of saved cities and towns to find out what's happening where your loved ones are &ndash; find it all in one simple and personalized view, with the option to include a picture of each individual, and also change their location at any time.

## Purpose
After many months of dedicated studying and working on smaller projects, WeatherFam represents my first large project; an attempt to apply what I've learned so far to something interesting and useful, and to push myself to learn a lot more, about production web apps, about Django, about the SDLC, and about what the day-to-day work of a SWE looks like.

When I came up with the idea for this project, I had my Mom in mind. With four sons that are now spread across the country (Maryland, New York, Illinois, and California), she always wants to know what kind of weather we're experiencing, so she knows we are safe and happy. Most weather apps are focused on seeing the forecast for one place at a time and providing every data point imaginable for that location. My goal was to bring only the pertinent information my Mom would want (temperature and primary weather event) into one simple, digestable view.

## Technology
The app is built on Django with a MySQL database. Weather data is retrieved from the Tomorrow.io API, and Google Maps API's are used for the location picking on a map and to obtain time zones for selected locations. The front end relies on Bootstrap, with a modest amount of custom CSS and JavaScript.

While currently developed on my local machine, in time, the site will use an AWS S3 bucket to store user-uploaded image files and then be deployed on Heroku.

# Demos
The following gifs from my local development demonstrate the basic functionality of the site.

## Home Page - Your Full WeatherFam!
*(Don't worry, these images are all stock photos!)*

<img src="demo-gifs/home.gif" width="100%"/>

<br>

## 1. Sign Up
*Please remember your password, as I don't currently have the option to reset your password by email*

<img src="demo-gifs/register.gif" width="100%"/>

<br>

## 2. Add a Person
*Add a name, upload an image (try to use a square image), pick the location on the map, and give the location a name*

<img src="demo-gifs/add-person.gif" width="100%"/>

<br>

## 3. Edit a Person
*Edit any of a person's name, image, location name, and/or location*

<img src="demo-gifs/edit-person.gif" width="100%"/>

<br>

# Deployment
I am currently working on deploying the app on Heroku and will post the link here when the production site is live!

<br>

# Future Development Ideas
While I originally intended for this project to be soley educational, I've become very interested in the app and believe it may actually be useful for myself and others. I am excited about the idea of continuing to work on it, rolling out new features and functionality over time. Some of the ideas I have are this point are:

- add a search box to the map to make it easier to choose a location
- save prior locations for each person and provide a dropdown to quickly switch between locations
- add a calendar feature for each person, so that trips or moves can be added to the calendar allowing the weather data to update accordingly
- determine if it's possible to request and use location data from location sharing apps, like FindMy on iOS, so a person's location updates as they move
- add a plug-in for the image upload to allow users to preview, crop, and resize before saving

This has been a very informative and fun project to work on, and I hope it continues to be so. I'd welcome any additional thoughts or feedback! Thanks.