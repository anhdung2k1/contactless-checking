#! /usr/bin/env python3
# -*- encoding: utf-8 -*-

import unittest
import os
import sys
import argparse

file_location = os.path.abspath(__file__)
root_directory = os.path.dirname(file_location)
default_helm_chart = os.path.join(root_directory, "..", "..", "build/helm-build/em-application/em-application")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tool to verify helm charts")
    parser.add_argument("--helmdir", help="The directory where helm chart is located",
                        default=default_helm_chart)
    parser.add_argument("--loglevel", default="info", help="The logging level to use (info|debug)")
    args = parser.parse_args()
    
    os.environ.setdefault("HELMDIR", args.helmdir)
    os.environ.setdefault("LOG_LEVEL", args.loglevel)
    
    loader = unittest.TestLoader()
    start_dir = root_directory
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner()
    result = not runner.run(suite).wasSuccessful()
    sys.exit(result)