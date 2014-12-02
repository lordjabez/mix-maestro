Overview
========

Mix Maestro is a system that provides a abstract HTTP JSON API (and accompanying web application) for a variety of digital mixing platforms. This API and GUI can be used by a variety of personal electronic devices (e.g. smartphones, tablets, laptops) to do basic control of the audio platform (e.g. monitor mixing) without requiring complicated, expensive, and proprietary personal mixing systems. It is designed to be plug and play with no configuration required.

Hardware
========

- Raspberry Pi Model A
- 4GB SD card
- 5.25v DC power adapter
- USB WiFi adapter with extended antenna
- RS-232 level shifter

Software
========

Server
------

- Python 3.3
- bottle WSGI microframework
- waitress webserver
- pyserial RS-232 package

Client
------

- HTML / CSS / JavaScript
- Ionic Frontend Framework
- AngularJS Application Framework
