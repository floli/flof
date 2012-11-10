#!/usr/bin/python2

import logging, optparse, os, sys

logger = logging.getLogger(__name__)
  
import common, configuration
from common import norm_path

from workers.baseworker import ContextManager,  WorkerRegistry, WorkerFactory, register_bundled_workers
from workers.workers import RootWorker

def add_options():
    """ Factory function for the OptionParser. """
    parser = optparse.OptionParser(usage="%prog [options] config_file")
    parser.add_option("-o", "--only", help="Execute only the named workers, separated by comma. 'case' worker is implicitly included.")
    parser.add_option("-n", "--not", dest="do_not", help="Do not execute the named workers, separated by comma.")
    parser.add_option("-c", "--context", help="Set a value in the context, format is key=value, comma seperated.")
    return parser


def parse_context(arg):
    """ Parses the --context argument from the command line. """
    context = {}
    try:
        for c in arg.split(","):
            s = c.split("=", 1)
            if len(s) == 2:
                context[s[0].strip()] = s[1].strip()
    except:
        pass
    
    return context


def main():
    oparser = add_options()
    (options, args) = oparser.parse_args()

    if not args:
        oparser.print_help()
        sys.exit()
    if not os.path.isfile(args[0]):
        print "Configuration file %s not existing." % args[0]
        sys.exit(-1)

    config_file = norm_path(args[0])
    config = configuration.parse_merge(config_file)
    loglevel = config.getroot().get("loglevel", 10)
    common.setup_logging("~/.flof/flof.log", loglevel)
 
    register_bundled_workers()

    if options.only:
        WorkerRegistry.workers = filter(lambda a: a in options.only.split(","), WorkerRegistry.workers)

    if options.do_not:
        WorkerRegistry.workers = filter(lambda a: a not in options.do_not.split(","), WorkerRegistry.workers)

    os.chdir(os.path.dirname(norm_path(args[0])))
    context = ContextManager({"config_file" : config_file})
    context.overrides = parse_context(options.context)
    RootWorker(config, context).run()
    

if __name__ == "__main__":
    main()
