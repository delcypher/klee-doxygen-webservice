from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import sys
import os
import logging
import signal

def main():
  """
      This program will run the GPUVerify Rise4Fun web service
      as a production server which uses Tornado as the HTTP
      server.
  """

  import argparse
  parser = argparse.ArgumentParser(description=main.__doc__)
  parser.add_argument('-p', '--port', type=int, default=55000, help='Port to use. Default %(default)s')
  parser.add_argument("-l","--log-level",type=str, default="INFO",choices=['debug','info','warning','error'])
  parser.add_argument("-o","--log-output",type=str, default='-', help='Write logging information to file. "-" means standard output. Default "%(default)s"')

  args = parser.parse_args()

  # Setup loging file
  logStream=None
  try:
    if args.log_output == '-':
      logStream=sys.stdout
    else:
      logStream = open(args.log_output,mode='a') # Append

    # Setup the root logger before importing app so that the loggers used in app
    # and its dependencies have a handler set
    logging.basicConfig(level=getattr(logging,args.log_level.upper(),None), 
                        stream=logStream,
                        format='%(asctime)s:%(name)s:%(levelname)s:%(module)s.%(funcName)s() : (PID %(process)d) %(message)s')
    logging.info("Starting KLEE Doxygen webservice")
    from webservice import app

    # Add signal handler for SIGTERM that will trigger the same exception that SIGINT does
    def terminate(signum,frame):
      logging.info("PID " + str(os.getpid()) + "Received signal " + str(signum))
      raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,terminate)

    try:
      logging.info("Starting server on port " + str(args.port))
      http_server = HTTPServer(WSGIContainer(app))
      http_server.bind(args.port)
      http_server.start(1) # Only allow one process, we don't want any races!
      IOLoop.instance().start()
    except KeyboardInterrupt:
      http_server.stop()

    logging.info("Exiting process:" + str(os.getpid()) )
  finally:
    logStream.close() 

if __name__ == '__main__':
  main()
  sys.exit(0)
