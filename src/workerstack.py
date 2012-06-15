import logging, threading
from ConfigParser import NoOptionError

logger = logging.getLogger(__name__)

import os, sys
import workers

class WorkerStack:
    """ Reads the configuration file, imports all workers and executes them.
    If a configuration file section contains an option 'class', try to import it, test if it is a subclass of workers.BaseWorker.
    A worker must contain a position attribute. This can be set in either the class itself or set/overwritten in the config file. """
    
    _workers = []
    _running_worker = None
    _sig_abort = threading.Event()
    
    def __init__(self, configuration):
        config = configuration

        for section in config.sections():
            try:
                class_str = config.get(section, "class")
            except NoOptionError:
                # This section does not have a class option, it's not describing a worker.
                continue
            try:
                module = __import__(class_str.split(".")[0])
                worker_cls = getattr(module, class_str.split(".")[1])
            except (ImportError, AttributeError):
                logger.warning("Can't import worker %s.", class_str)
            else:
                if not issubclass(worker_cls, workers.BaseWorker):
                    logger.warning("Object %s not a subclass of BaseWorker. Discarding.", class_str)
                    continue
                if config.has_option(section, "position"):
                    position = config.getint(section, "position")
                elif hasattr(worker_cls, "position"):
                    position = worker_cls.position
                else:
                    logger.warning("Worker %s has no position assigned. Discarding.", class_str)
                    continue
                if config.getboolean(section, "do"):
                    worker_obj = worker_cls(section, config.option_dict(section), {"configuration": config})
                    worker_obj.position = position
                    logger.debug("Added worker %s, position %i, name %s", class_str, worker_obj.position, worker_obj.name)
                    self._workers.append( worker_obj )

        self._workers.sort(key = lambda a: a.position)
        
        
    def pop_worker(self, max_pos = sys.maxint):
        """ Returns the next object in order up to max_pos. """
        if self._workers and self._workers[0].position < max_pos:
            return self._workers.pop(0) 
        else:
            return None

    def workers(self, max_pos = sys.maxint):
        """ Generator function that yields a list of all workers up to max_pos in correct order. """
        while True:
            worker = self.pop_worker(max_pos)
            if worker == None:
                break
            else:
                yield worker

    def execute(self, max_pos = sys.maxint):
        """ Executes the workers up to max_pos. """
        for worker in self.workers(max_pos):
            if self._sig_abort.is_set():
                logger.debug("Abort signal is set, worker execution loop stopped.")
                break
            elif worker.do():
                logger.info("Executing worker %s.", worker.name)
                self._running_worker = worker
                cwd = os.getcwd()
                if os.path.isdir(worker.case):
                    os.chdir(worker.case)
                worker.run()
                os.chdir(cwd)
                self._running_worker = None
            else:
                logger.info("Not executing worker %s", worker.name)


    def active_worker(self):
        """ Returns the name of the worker currently running, if not worker is running, returns "" """
        if self._running_worker == None:
            return ""
        else:
            return self._running_worker.name

    def worker_info(self):
        """ Returns a dictionary of worker specific info, e.g. timestep. """
        return self._running_worker.info()


    def get_worker_by_type(self, type_name):
        """ Returns the worker that is of type type_name. type_name is a python class. """
        for worker in self.workers():
            if isinstance(worker, type_name):
                return worker


    def abort(self):
        """ Aborts execution of the current worker and all further workers. """
        self._sig_abort.set()
        if self._running_worker:
            self._running_worker.abort()
