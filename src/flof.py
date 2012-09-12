#!/usr/bin/python2

import logging, optparse, os, sys, threading, traceback

logger = logging.getLogger(__name__)
  
import common, configuration
from common import norm_path

from workers.baseworker import WorkerFactory, register_bundled_workers

from workers.foamutility import ChangeDictionary

import xml.etree.ElementTree as ET


def add_options():
    """ Factory function for the OptionParser. """
    parser = optparse.OptionParser(usage="%prog [options] config_file")
    parser.add_option("-f", "--file", help="Save the pyFoamCaseBuilder file to the given location and exit.")
    parser.add_option("-c", "--config", help="Add/overwrite configuration options. Syntax: 'section.key=value,...'")
    return parser


def main():
    common.setup_logging("~/.flof/flof.log")

    oparser = add_options()
    (options, args) = oparser.parse_args()

    if not args:
        oparser.print_help()
        sys.exit()
    if not os.path.isfile(args[0]):
        print "Configuration file %s not existing." % args[0]
        sys.exit(-1)


    register_bundled_workers()
    
    config = ET.parse(args[0])
    os.chdir(os.path.dirname(norm_path(args[0])))

    wf = WorkerFactory(config)

    for w in wf.workers():
        if w.do:
            w.run()
    

if __name__ == "__main__":
    main()
