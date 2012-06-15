import logging

ST_QUEUED, ST_RUNNING, ST_FINISHED, ST_STOPPED, ST_ABORTED, ST_FAILED = 0, 1, 2, 3, 4, 5


def getboolean(str_val):
    """ Converts a str_val to a boolean value, taken from ConfigParser.py. """
    boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                       '0': False, 'no': False, 'false': False, 'off': False}
    if type(str_val) == bool:
        return str_val
    
    if str_val.lower() not in boolean_states:
            raise ValueError, 'Not a boolean: %s' % str_val
    return boolean_states[str_val.lower()]

def state2str(state):
    """ Converts a numerical job/queue state to the describing string. """
    mapping = {ST_QUEUED:"Queued", ST_RUNNING:"Running",
               ST_FINISHED:"Finished", ST_STOPPED:"Stopped",
               ST_ABORTED:"Aborted", ST_FAILED:"Failed"}
    return mapping[state]

import os

def norm_path(*parts):
    """ Returns the normalized, absolute, expanded and joint path, assembled of all parts. """
    return os.path.abspath(os.path.expanduser(os.path.join(*parts)))


def setup_logging(logfile):
    """ Setup the logging. Should be called at the beginning of every execution (which is flof.py and flofsever.py only at this time). """
    FORMAT = "%(asctime)s - %(name)s:%(levelname)s - %(message)s"
    logfile = norm_path(logfile)
    logging.basicConfig(level = logging.DEBUG, format=FORMAT, filename = logfile)
    ch  = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(FORMAT))
    logging.getLogger().addHandler(ch)


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """ Mixin construced from ThreadingMixIn and SimpleXMLRPCServer. """
    pass
