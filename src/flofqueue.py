#!/usr/bin/python2

import xmlrpclib, sys
from common import norm_path, state2str, ST_RUNNING
from configuration import Configuration

config = Configuration()
port = config.getint("general", "server_port")

proxy = xmlrpclib.ServerProxy("http://localhost:%i/" % port, allow_none = True)


def list_queue():
    """ Gives a list of enquened jobs and their status. """
    queue = proxy.get_queue()

    print "Queue State: ", state2str(proxy.queue_state())
    print "Queue Size:  ", len(queue)
    print ""
    
    fmt_str = "{jid!s:8}{config:60}{prio!s:10}{state:5}"
    run_fmt_str = "        Active Worker: {active_worker:44} Worker Information: {worker_info}"
    print fmt_str.format(jid="Job ID", config="Configuration File", prio="Priority", state="State")
    print "---------------------------------------------------------------------------------------"
    for i in queue:
        state = i["state"]
        i["state"] = state2str(i["state"])
        print fmt_str.format(**i)

        if state == ST_RUNNING:
            print run_fmt_str.format(**i)
            print ""
    print ""
    
def start():
    """ Starts the queue. """
    print "Starting queue."
    proxy.start_queue()

def stop():
    """ Stop the queue. Does not effect currently running jobs. """
    print "Stopping queue."
    proxy.stop_queue()

def abort():
    """ Aborts the job. Assumes that there is only one job running at a time. """
    queue = proxy.get_queue()
    for i in queue:
        if i["state"] == ST_RUNNING:
            proxy.abort(i["jid"])
            print "Job %s aborted" % i["jid"]
            return

    print "Can't abort, not running jobs."

def put(case_config, prio):
    case_config = norm_path(case_config)
    print "Put case with config %s, priority %s in the queue." % (case_config, prio)
    jid = proxy.enqueue(prio, case_config)
    print "Queued job with ID", jid

    
def delete(jid):
    """ Deletes the given job. """
    print "Delete", jid
    print proxy.delete(jid)

def repriorize(jid, new_prio):
    """ Change the priority of the given job. """
    print "Repriorize job" , jid, new_prio
    print proxy.reprio(jid, new_prio)
 

def help():
    print "Usage:", sys.argv[0], "action <arguments>\n"
    print "action can be:\n"
    print "list                            List queued jobs."
    print "start                           Start the queue."
    print "stop                            Stops the queue. Currently running jobs are not affected."
    print "abort                           Aborts the currently running job."
    print "put <case config file> [prio]   Puts the specified case control file with a priority in the queue. prio is optional, default is 10."
    print "del <jid>                       Removes a job from the queue given by the job id."
    print "reprio <jid> <prio>             Repriorize a job."
    
def main():
    try:
        action = sys.argv[1]

        if action == "list":
            list_queue()
        elif action == "start":
            start()
        elif action == "stop":
            stop()
        elif action == "abort":
            abort()
        elif action == "put":
            sys.argv.append("10") # Just put the default value, if it is given, it's ignored by the next line.
            put(*sys.argv[2:4])
        elif action == "del":
            delete(sys.argv[2])
        elif action == "reprio":
            repriorize(*sys.argv[2:4])
  
        else:
            help()
    except (IndexError, TypeError):
        help()
        
if __name__ == "__main__":
    main()
