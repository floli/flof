#!/usr/bin/python2

import logging, optparse

logger = logging.getLogger(__name__)

import common, jobqueue
from configuration import Configuration


class FlofServer():
    """ FlofServer works as a XMLRPC-Server. It is controlled by flofqueue.py and manages the queue.  """
    jobqueue = jobqueue.JobQueue()

    def __init__(self, config):
        port = config.getint("general", "server_port")
        server = common.ThreadedXMLRPCServer( ('', port), allow_none = True, logRequests=False )
        server.register_introspection_functions()
        server.register_instance(self)
        logger.info("flofserver listening on port %i.", port)
        server.serve_forever()       
                    
    def enqueue(self, prio, case_config):
        """ Enqueue a new job with given priority. case_config is a string to the configuration file. """
        ret = self.jobqueue.put( jobqueue.Job(prio, case_config) )
        return ret

    def start_queue(self):
        """ Starts the queue. Initial state of queue is stopped. """
        return self.jobqueue.start()

    def stop_queue(self):
        """ Stops the queue. """
        return self.jobqueue.stop()

    def queue_state(self):
        """ Returns the state of the queue, either ST_RUNNING or ST_STOPPED. """
        return self.jobqueue.state()
    
    def delete(self, jid):
        """ Delete a specific job, given by the job ID from the queue. """
        return self.jobqueue.delete(jid)
    
    def get_queue(self):
        """ Returns the entire queue as a list of jobs. Each job is represented by a dictionary. """
        return self.jobqueue.as_dict()

    def abort(self, jid):
        """ Aborts a job. Do nothing, if the job is not running. """
        self.jobqueue.abort(jid)
        return 0

    def reprio(self, jid, new_prio):
        """ Change the priority of the given job. """
        return self.jobqueue.reprio(jid, new_prio)

def add_options():
    """ Factory function for the OptionParser for command line parsing. """
    parser = optparse.OptionParser(usage="%prog [options]")
    parser.add_option("-c", "--config", help="Add/overwrite configuration options. Syntax: 'section.key=value,...'")
    return parser

    
if __name__ == "__main__":
    common.setup_logging("~/.flof/flofserver.log")
    oparser = add_options()
    (options, args) = oparser.parse_args()
    configuration = Configuration(cmd_config = options.config)
    FlofServer(configuration)
