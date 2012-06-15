import itertools, logging, subprocess, threading, time, xmlrpclib

logger = logging.getLogger(__name__)

from configuration import Configuration

import common
from common import ST_QUEUED, ST_RUNNING, ST_FINISHED, ST_STOPPED, ST_ABORTED, ST_FAILED


generate_jid = itertools.count(1).next

class Job:
    """ Represents a job. Starts flof.py and connects to it. """
    _connection = None
    _child_proc = None
    
    def __init__(self, prio, config):
        self.prio = int(prio)
        self.config = Configuration(config)
        self.jid = generate_jid()

    def run(self):
        """ Runs the job asynchronously by calling 'flof.py --no-run config_file'. """
        assert self.state == ST_QUEUED

        self._child_proc = subprocess.Popen(["flof.py", "--no-run", self.config.case_config])
        time.sleep(2) # Wait some seconds to allow server to start
        logger.info("Job %s started: %s", str(self.jid), self.config.case_config)

        self._connection = xmlrpclib.ServerProxy("http://localhost:%i/" %
                                                 self.config.getint("general", "slave_port"),
                                                 allow_none = True)
        try:
            self._connection.run() 
        except:
            logger.warning("Exception raised while running the flof client. This may happen if a run is aborted.")
        

    @property
    def state(self):
        if self._child_proc == None:
            return ST_QUEUED
        elif self._child_proc.poll() == None:
            return ST_RUNNING
        elif self._child_proc.returncode == ST_ABORTED:
            return ST_ABORTED
        elif self._child_proc.returncode == 0:
            return ST_FINISHED
        elif self._child_proc.returncode != 0:
            return ST_FAILED
        
    def abort(self, force=False):
        """ Aborts the job. If force is True the process is simply killed. Otherwise a XML-RPC call to abort is send. """
        if force:
            if self._child_proc and not self._child_proc.poll():
                self._child_proc.kill()
        else:
            try:
                self._connection.abort()
            except:
                pass
       
    def active_worker(self):
        """ Returns the name of the currently active worker. """
        try:
            return self._connection.active_worker()
        except:
            return ""  # Return None??

    def worker_info(self):
        """ A dictionary with information that is specific to the currently running worker. """
        try:
            return self._connection.worker_info()
        except:
            return {}
        
       
    def as_dict(self):
        """ Dictionary with job specific information. """
        return {
            "jid": self.jid,
            "prio": self.prio,
            "config": self.config.case_config,
            "state": self.state,
            "active_worker" : self.active_worker(),
            "worker_info" : self.worker_info()
            }

class JobQueue:
    """ Implementation of a Queue, neither thread safe nor efficient. """
    
    _queue = []
    _stopqueue_event = threading.Event()
    _poll_thread = threading.Thread()

    def start_next(self):
        """ Launches the next job in the queue. """
        self.sort()
        queued = [i for i in self._queue if i.state == ST_QUEUED]
        if queued:
            queued[0].run()
            return queued[0].jid
        else:
            return False
    
    def sort(self, reverse = False):
        """ Sort by priority """
        self._queue.sort(key = lambda a: (a.state, -a.prio), reverse=reverse) 
        
    def put(self, job):
        self._queue.append(job)
        logger.debug("Job %s addded to queue", job.as_dict())
        return job.jid
            
    def delete(self, jid):
        """ Delete the specified job. """
        for n, i in enumerate(self._queue):
            if i.jid == int(jid):
                del self._queue[n]
                logger.info("Job %s deleted." % jid)
                return jid
            
        logger.warning("Trying to delete non-existent job %s." % jid)
        return 0

    def abort(self, jid):
        """ Aborts the job with the job id jid. """
        for i in self._queue:
            if i.jid == int(jid):
                logger.info("Job %s aborted.", jid)
                i.abort()

    def reprio(self, jid, new_prio):
        """ Change the priority of the given job. """
        for i in self._queue:
            if i.jid == int(jid):
                i.prio = int(new_prio)
                self.sort
                logger.info("Priority of job %s changed to %s.", jid, new_prio)
                return i.jid
        return -1
                
    def as_dict(self):
        """ Returns the entire queue as a list of jobs. Each job is represented by a dictionary. """
        self.sort()
        return [i.as_dict() for i in self._queue]

    def running_jobs(self):
        """ Lists all currently running jobs. """
        return [job for job in self._queue if job.state == ST_RUNNING]


    def start(self):
        """ Starts the queue. """
        if self._poll_thread.is_alive():
            logger.warning("Queue already started.")
            return False
        else:
            self._stopqueue_event.clear()
            self._poll_thread = threading.Thread(target=self._poll_queue)
            self._poll_thread.daemon = True
            self._poll_thread.start()
            logger.info("Queue started.")
            return True

    def stop(self):
        """ Stops the queue. Does not affect running jobs. """
        self._stopqueue_event.set()
        logger.info("Stopping queue.")
        return True

    def state(self):
        """ Returns the state of the queue, either ST_RUNNING or ST_STOPPED. """
        if self._poll_thread.is_alive():
            return ST_RUNNING
        else:
            return ST_STOPPED
    
    def _poll_queue(self):
        """ Checks for jobs to run. If the event is set, the threads exits and the queue has stopped
        Otherwise it will wait for timeout 10 seconds. """

        # second isSet() test is needed since python <2.7 returns always None from wait()
        while not self._stopqueue_event.wait(10) and not self._stopqueue_event.isSet():
            if not self.running_jobs():
                self.start_next()

        logger.info("Queue stopped")


