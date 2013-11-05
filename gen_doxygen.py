#!/usr/bin/env python2.7
import sys
import os
import shutil
import subprocess
import logging

# Load configuration
from config import *

# Handy function for building enums
def enum(*sequential):
    #Build a dictionary that maps sequential[i] => i
    enums = dict( zip(sequential, range(len(sequential))) )
    #Build a reverse dictionary
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverseMapping'] = reverse
    return type('Enum', (object,) , enums)

# Return codes used
returnCode = enum('ok',
                  'failedClone',
                  'invalidGitRepi',
                  'updateFailed',
                  'configureFailed',
                  'doxygenFailed',
                  'copyFail'
                 )

def runCmd(cmdline, workingDir=None):
    if workingDir == None:
        workingDir = os.getcwd()

    if not ( os.path.exists(workingDir) and os.path.isdir(workingDir)):
        logging.error('Working directory "{0}" does not exist'.format(workingDir))
        return 1

    logging.info('Running ' + str(cmdline))
    if logging.getLogger().level <= logging.DEBUG:
        return subprocess.call(cmdline, cwd=workingDir)
    else:
        # Disregard tool's stdout/stderr
        with open(os.devnull, 'w') as nullFile:
            return subprocess.call(cmdline, cwd=workingDir, stdout=nullFile, stderr=nullFile)

def isGitRepo(path):
    if not os.path.exists( os.path.join(path, '.git') ):
        return False

    if runCmd(['git', 'status'], path) == 0:
        return True
    else:
        return False

def updateNeeded(commitHash):
    currentCommitHash = subprocess.check_output(['git','rev-parse','HEAD'], cwd=repoDest)
    currentCommitHash = str(currentCommitHash)
    logging.debug('Current commit hash is "{0}"'.format(currentCommitHash))
    logging.debug('Comparing to hash {0}'.format(commitHash))
    if commitHash != currentCommitHash:
        return True
    else:
        return False


def run():
    logging.info('Starting build process')
    workingDir=os.path.dirname(__file__)

    if not os.path.exists(repoDest):
        logging.info('Repository does not exist')

        if runCmd(['git', 'clone', repoURL, repoDest], workingDir) != 0:
            return returnCode.failedClone

    if not isGitRepo(repoDest):
        logging.error('Invalid git repository')
        return returnCode.invalidGitRepo

    # Force update
    runCmd(['git','checkout', 'master'], repoDest)
    logging.info('Forcing update')
    if runCmd(['git', 'pull', '--force', 'origin'], repoDest) != 0:
        return returnCode.updateFailed

    # If old repo exists delete it
    if not os.path.exists(buildDir):
        logging.info('Creating new direction "{0}"'.format(buildDir))
        os.mkdir(buildDir)

    # CD into buildDir
    os.chdir(buildDir)

    # Configure
    result=0
    if os.path.exists('config.status'):
        result = runCmd([ os.path.join('.', 'config.status') ])
    else:
        result = runCmd([ os.path.join(repoDest, 'configure')] + configureFlags)
    
    if result != 0:
        logging.error('Configure failed')
        return returnCode.configureFailed

    # Build doxygen
    logging.debug('Building docs')
    if runCmd(['make', 'doxygen'], os.getcwd()) != 0:
        logging.error('Failed to generate doxygen')
        return returnCode.doxygenFailed

    # Copy doxygen docs

    if not os.path.exists(doxygenDest):
        os.mkdir(doxygenDest)

    # Use rsync to do the copy
    logLevel=logging.getLogger().level
    logging.debug('Copying docs')
    if runCmd(['rsync', 
               '--verbose' if logLevel <= logging.DEBUG else '', # Only be verbose if we are debugging
               '--recursive',
               '--safe-links',
               '--inplace',
               os.path.join(buildDir, 'docs','doxygen','html/'), # source (trailing slash is important)
               doxygenDest # Destination
              ]) != 0:
        logging.error('Failed to copy doxygen files')
        return returnCode.copyFail
                
    return returnCode.ok

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(run())
