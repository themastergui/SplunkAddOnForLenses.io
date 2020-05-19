#!/usr/bin/env python3

# Developped by guillaume.ayme@gmail.com. @lemastergui on Twitter
# Script is main wrapper for Splunk custom command. Will call lenses.py script passing as arguments a SQL statement, target URL (Lenses.io instance) and env variable where the security token is stored. Before running the lenses.py script, it will take some settings from the ta_addon_for_lenses_io_settings.conf. See README for more details

from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import json
import re
from splunklib import six


import traceback

import os
import subprocess
import splunk
from subprocess import Popen
from logging import getLogger

#sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

import splunk.entity as entity
import splunklib.client as client
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration(generates_timeorder=True)
class LensesCustomCommand(GeneratingCommand):
    """ %(synopsis)
    ##Syntax
    %(syntax)
    ##Description
    %(description)
    """
    sql = Option(require=True)

    def generate(self):
       sql = self.sql
       _logger = getLogger("LensesCustomCommand")
       _logger.info("Running Lenses.io custom command")

       try:
         confFile = self.service.confs['ta_addon_for_lenses_io_settings']
         stanza = confFile["additional_parameters"]
         lensesUrl = stanza["lenses_io_url"]
         pythonPath = stanza["lenses_python"]
         lensesTimeout = int(stanza["lenses_timeout"])
         _logger.info("Lenses custom command lenses_io_url from conf file is %s" %lensesUrl)
       except Exception as e:
         _logger.error("error when trying to get conf from ta_addon_for_lenses_io_settings.conf file: %s" %e)
         pass
       if not lensesUrl:
          _logger.error("could not find lenses_io_url in ta_addon_for_lenses_io_settings.conf. Ensure it TA has been configured correctly")



       storage_passwords=self.service.storage_passwords
       for credential in storage_passwords:
          if credential.realm=="__REST_CREDENTIAL__#TA-addon_for_lenses_io#configs/conf-ta_addon_for_lenses_io_settings":
             try:
               serviceTokenClear = credential.content.get('clear_password')
# NOTE: Be careful if uncommenting the next line. It will show token in clear text in search.log
#               _logger.error("Lenses.io token configured is is %s" %serviceTokenClear)
               serviceTokenJson = json.loads(serviceTokenClear)
               serviceToken  = serviceTokenJson['password']
             except Exception as e:
               _logger.error("e is %s" %e)
               _logger.warning("found an incorrect passord or  password that doesn't look like a token for Lenses.io. Ensure it has been set in Addon Configuration. Or otherwise may find another password that matches shortly... Also ensure you have entered the token correctly and it's prefixed with the name of the service account name such as <name>:<token>")
          else:
             _logger.error("Could not find service token to connect to Lenses.io. Ensure it has been configured in the App settings")

       lensesScriptPath = os.path.join(sys.path[0], 'lenses.py')
      
       _logger.info("About to launch command. path is %s, token is **masked**, url is %s, sql is %s" %(lensesScriptPath,lensesUrl,sql))
    
       #Save token in env variable. It will be accessed by lenses.py script later
       os.environ['LENSES_TOKEN'] = serviceToken
    
      # Now we can run our command. We pass as arguments the name of the ENV Variable that holds the security token
       process = Popen([pythonPath, "-E", lensesScriptPath, "-c", "LENSES_TOKEN" , "-u", lensesUrl, "-s", sql],stderr=subprocess.PIPE, stdout=subprocess.PIPE)

       try:
         outs, errs = process.communicate(timeout=lensesTimeout)
       except subprocess.TimeoutExpired:
         _logger.error("timeout error calling lenses python command.")
         raise Exception("timeout error when calling lenses.py script. See search.log.")
       if process.returncode != 0:
         _logger.error("error calling lenses python command. error was %s " %errs)
         raise Exception("Error when calling lenses.py script. See search.log. error: %s" %errs)

       _logger.error("standard error is %s" %errs)
       _logger.error("standard out is %s" %outs)
       resultsUtf = outs.decode('utf-8')
       #resultsUtf = results.decode('utf-8')
       _logger.debug("Lenses custom command results are %s" %resultsUtf)
       try:
         resultsJson = json.dumps(resultsUtf)
         resultsJson = json.loads(resultsUtf)
       except Exception as e:
          _logger.error("no results returned by Lenses.io custom command")
          _logger.error("returned values were %s" %e)
          raise Exception("Could not process data returned from Lenses. See search.log. error %s" %e)
       for result in resultsJson:
         yield {'_serial': "1", '_time': int(result["metadata"]["timestamp"])/1000, '_raw': result}
       pass

dispatch(LensesCustomCommand, sys.argv, sys.stdin, sys.stdout, __name__)
