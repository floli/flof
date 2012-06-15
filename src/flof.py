#!/usr/bin/python2

import logging, optparse, os, sys, threading, traceback

logger = logging.getLogger(__name__)
  
import common, configuration
from common import norm_path

from workerstack import WorkerStack
from workers import Casebuilder


class ControlServer():
    """ XML-RPC Server that is used to get information about the actions flof is performing.
    All methods are exposed to the RPC interface. """

    returncode = 0

    def __init__(self, config, worker_stack, auto_run = False):
        self.w_stack = worker_stack
        
        port = config.getint("general", "slave_port")
        self.server = common.ThreadedXMLRPCServer( ('', port), allow_none = True, logRequests=False )
        self.server.register_introspection_functions()
        self.server.register_instance(self)
        self.server.daemon_threads = True # Threads are killed when shutdown initiated.
        logger.info("flof listening on port %i.", port)
        if auto_run:
            t = threading.Thread(target=self.run)
            t.daemon = True
            t.start()
        self.server.serve_forever()

    def run(self):
        """ Starts the job. The function itself is blocking, but the server is threaded.
        Shutdown after execution. """

        try:
            self.w_stack.execute()
        except: # Since run() is a seperate thread any exception not caught here will be lost.
            traceback.print_exc()
        finally: # Make sure the server is always shut down.
            self.server.shutdown()
        
    def abort(self):
        """ Aborts the job, quits the programm. """
        self.returncode = common.ST_ABORTED
        logger.info("Got abort signal, initiating shut down.")
        self.w_stack.abort()
        print "Returned from w_stack.abort"
                

    def worker_info(self):
        """ Returns a info dict that is custom to the worker, e.g. timestep. """
        return self.w_stack.worker_info()

    def active_worker(self):
        """ Returns the worker that is currently running. """
        return self.w_stack.active_worker()
        

def add_options():
    """ Factory function for the OptionParser. """
    parser = optparse.OptionParser(usage="%prog [options] config_file")
    parser.add_option("-f", "--file", help="Save the pyFoamCaseBuilder file to the given location and exit.")
    parser.add_option("-c", "--config", help="Add/overwrite configuration options. Syntax: 'section.key=value,...'")
    parser.add_option("-n", "--no-run", help="Do not run the case. The run must be initiated through the XML-RPC method run().", action="store_true", dest="no_run")
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
        
    config = configuration.Configuration(args[0], options.config)
    os.chdir(os.path.dirname(norm_path(args[0])))

    w_stack = WorkerStack(config)
    
    if options.file:
        f = open(norm_path(options.file), "w")
        cbw = w_stack.get_worker_by_type(Casebuilder)
        cbw.create_pfcb(f, cbw.config["case_template"])
        sys.exit()
    
    server = ControlServer(config, w_stack, not options.no_run)

    sys.exit(server.returncode)
    

if __name__ == "__main__":
    main()
