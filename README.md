KLEE Doxygen web service
========================

This is a simple python web application built on top of Flask that creates a
simple server to act as a receiver for post-receive notifications from GitHub.

It's specific goal is to regenerate doxygen documentation for the KLEE project
when necessary (i.e. when a new commit is made).

Configuration
=============

To configure copy config.py.template to config.py and set the variables
appropriately.

Running
=======

To run use

$ ./webservice.py --public
