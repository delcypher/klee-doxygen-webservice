KLEE Doxygen web service
========================

This is a simple python web application built on top of Flask and Tornado that
creates a simple server to act as a receiver for post-receive notifications
from GitHub.

It's specific goal is to regenerate doxygen documentation for the KLEE project
when necessary (i.e. when a new commit is made).

Configuration
=============

To configure copy config.py.template to config.py and set the variables
appropriately.

Debugging
=========

Use the development server (use --public if it needs to be tested with the outside world)

$ python webservice.py --debug


Production
==========

Use the production server (uses Tornado HTTP server).

$ python production_server.py
