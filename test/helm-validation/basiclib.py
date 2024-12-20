#! /usr/bin/python3
# -*- encoding: utf-8 -*-

import os
import subprocess
import shlex
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if "LOG_LEVEL" in os.environ:
    logger.setLevel(os.environ.get("LOG_LEVEL").upper())

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
if "LOG_LEVEL" in os.environ:
    handler.setLevel(os.environ.get("LOG_LEVEL").upper())
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def exec(command):
    """
    Snippet to run shell commands and get back its output
    Args:
        command (str): run commands
    """
    logger.debug("EXEC: %s", command)
    try:
        result = subprocess.check_output(shlex.split(command), encoding="utf-8", stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise ShellError(e)
    logger.debug("EXEC-RESULT: %s", result)
    return result

def loginfo(message, *args, **kwargs):
    logger.info(message, *args, **kwargs)
    
def logdebug(message, *args, **kwargs):
    logger.debug(message, *args, **kwargs)
    
def logerror(message, *args, **kwargs):
    logger.error(message, *args, **kwargs)
    
class ShellError(Exception):
    def __init__(self, error):
        error_details = (
            "\n## ERROR DETAILS ##\n"
            f"COMMAND: {' '.join(error.cmd)}\n"
            f"OUTPUT: {error.output.rstrip()}\n"
            f"EXIT CODE: {error.returncode}"
        )
        super().__init__(error_details)