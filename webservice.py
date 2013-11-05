#!/usr/bin/env python2.7
from flask import Flask, jsonify, url_for, request, abort, make_response
from socket import gethostname
import logging
import pprint
import json
import gen_doxygen
import traceback

app = Flask(__name__)

@app.route('/post-receive', methods=['POST'])
def handlePostReceive():
    logging.debug('Headers:' + pprint.pformat(request.headers))
    commitData = None
    responseString='No payload'

    # GitHub specific...
    if 'payload' in request.form:
        try:
            logging.debug('stuff:' + str(request.form['payload']))
            commitData = json.loads(request.form['payload'])

            logging.debug('Loaded commit data:\n{0}'.format( pprint.pformat(commitData)))

            result = gen_doxygen.returnCode.ok

            # Get newest commit hash
            newCommit = commitData['head_commit']['id']
            logging.info('Latest upstream commit "{0}"'.format(newCommit))
            if gen_doxygen.updateNeeded(newCommit):
                logging.info('Generating Doxgyen docs')
                result = gen_doxygen.run()
            else:
                logging.info('No need to regenerate docs')

            logging.info('Done')

            responceString = gen_doxygen.returnCode.reverseMapping[result]
            logging.info('Result of generating docs:' + responceString)
        except Exception as e:
            responceString = 'Exception occured:' + traceback.format_exc()
            logging.error(responceString)
    else:
        logging.debug('No payload')


    # Return some sort of response...
    return make_response(jsonify( { 'status': responseString } ))

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)

if __name__ == '__main__':
        logging.basicConfig(level=logging.INFO)
        import argparse
        parser = argparse.ArgumentParser(description='Run Development version')
        parser.add_argument('-p', '--port', type=int, default=55000, help='Port to use. Default %(default)s')
        parser.add_argument('-d', '--debug', action='store_true',default=False, help='Use Flask Debug mode and show debugging output. Default %(default)s')
        parser.add_argument('--public', action='store_true', default=False, help='Make publically accessible. Default %(default)s')
        parser.add_argument('-s','--server-name', type=str, default='localhost' , help='Set server hostname. This is ignored is --public is used. Default "%(default)s"')

        args = parser.parse_args()


        if args.debug:
            print("Using Debug mode")
            logging.getLogger().setLevel(logging.DEBUG)

        # extra options
        options = { }
        if args.public:
            options['host'] = '0.0.0.0'
            app.config['SERVER_NAME'] = gethostname() + ':' + str(args.port)
        else:
            app.config['SERVER_NAME'] = args.server_name + ':' + str(args.port)

        print("Setting SERVER_NAME to " + app.config['SERVER_NAME'])

        app.run(debug=args.debug, port=args.port, **options)
