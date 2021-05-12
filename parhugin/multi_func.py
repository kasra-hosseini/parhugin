#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "Kasra Hosseini"
__license__ = "MIT License"

from collections import deque
import multiprocessing
import time
from typing import Union, Sequence
from .utils import Process as myProcess
from .utils import cprint, bc

class multiFunc:

    def __init__(self, num_req_p: Union[int, None]=None, 
                 sleep_time: float=0.1,
                 max_queue_length: int=10):
        """Instantiate multiFunc

        Parameters
        ----------
        num_req_p : Union[int, None], optional
            Number of parallel processes, by default None
            if None, number of CPUs will be used instead
        sleep_time : float, optional
            time interval between checking the availability of processes, by default 0.1
        """
        if num_req_p == None:
            num_req_p = multiprocessing.cpu_count()
            print(f"[INFO] num_req_p was not set by the user. It is set to {num_req_p}.")
        else:
            print(f"[INFO] #requested processes: {num_req_p}")
        self.num_req_p = num_req_p
        self.sleep_time = sleep_time
        self.num_running_p = 0
        self.queue = deque()
        self.jobs = []
        self._pointer = None
        self._jobs_pointer = None
        self._queue_pointer = None
        # The variable max_queue_length is used to check:
        # (self.num_running_p + self.num_remain_p) < self.max_queue_length
        self.max_queue_length = max(max_queue_length, num_req_p)
    
    def add_job(self, target_func, target_args: Sequence):
        """Add a job to the list of jobs

        Parameters
        ----------
        target_func
            Serial version of the function to be parallelized
        target_args : Sequence
            Arguments of the function (serial version)
        """
        self.queue.append([target_func, target_args])
        #p = myProcess(target=target_func, args=target_args)
        #self.jobs.append(p)

    def add_list_jobs(self, list_jobs: Sequence):
        """Add a list of jobs

        Parameters
        ----------
        list_jobs : Sequence
            list_jobs contains:
            [   
                [func1, (arg1_1, arg2_1, arg3_1)],
                [func1, (arg1_2, arg2_2, arg3_2)],  
                [func2, (...)],
                ...
            ] 
        """
        for one_job in list_jobs:
            self.add_job(target_func=one_job[0], target_args=one_job[1])
    
    def check_jobs(self):
        """
        Check the number of running/finished/remained jobs

        In parhugin, self.queue keeps track of all jobs to be run
        Jobs are added from queue to ---> self.jobs (list)
        
        The following variables are all computed based on self.jobs:
        num_running_p, num_finished_p, num_remain_p, num_exceptions_p

        ATTENTION: num_remain_p can be 0 but len(self.queue) != 0
                   The reason is that num_remain_p is computed based on self.jobs
        """
        self.num_running_p = 0
        self.num_finished_p = 0
        self.num_remain_p = 0
        self.num_exceptions_p = 0
        for proc in self.jobs:
            if proc.exception:
                self.num_exceptions_p += 1
            if proc.is_alive():
                self.num_running_p += 1
            elif proc._popen == None:
                self.num_remain_p += 1
            else:
                self.num_finished_p += 1
    
    def run_jobs_index(self, i1: int, i2: int, verbosity: int=1):
        """Run jobs from i1 to i2 indices

        Parameters
        ----------
        i1 : int
            index 1
        i2 : int
            index 2 
        verbosity : int, optional
            Level of verbosity for output:
            0: no message
            1 (default): minimal (e.g., info on start/end jobs)
            2: info on running/finished/remained jobs after each start_job
            3: info after every check_jobs! (lots of lines)
        """
        assert (i2 > i1 >= 0), f"{i2} should be larger than {i1} and {i1} should be >= 0"
        assert (i2 <= len(self.queue)), f"{i2} is more than the number of jobs ({len(self.queue)})"

        self._pointer = i1
        self._queue_pointer = i1
        self._jobs_pointer = 0
        self.job_start_time = time.time() 
        while self._pointer < i2:
            self.start_job(verbosity=verbosity)
            time.sleep(self.sleep_time)
        self.join_all()

        #self._print_job_info()
        self.job_elapsed_time = time.time() - self.job_start_time
        if verbosity >= 1:
            print(f"Total time: {self.job_elapsed_time}")
        self._print_exceptions()

    def run_jobs(self, verbosity: int=1):
        """Run all the jobs in self.jobs, refer to run_jobs_index for more info"""
        self.run_jobs_index(0, len(self.queue), verbosity)
    
    def start_job(self, verbosity: int=1):
        """Start a process after checking:
           1. number of running processes is less than the number of requested processes
           2. the requested process is not alive or has not been done before

        verbosity : int, optional
            Level of verbosity for output:
            0: no message
            1 (default): minimal (e.g., info on start/end jobs)
            2: info on running/finished/remained jobs after each start_job
            3: info after every check_jobs! (lots of lines)
        """
        
        self.check_jobs()
        if self.num_finished_p > self.max_queue_length:
            tmp_running_p = [proc for proc in self.jobs if proc.is_alive()] 
            tmp_remain_p = [proc for proc in self.jobs if ((not proc.is_alive()) and (proc._popen == None))] 
            self.jobs = []
            self.jobs = tmp_running_p + tmp_remain_p
            self._jobs_pointer = len(tmp_running_p)

        self.check_jobs()
        while ((self.num_running_p + self.num_remain_p) < self.max_queue_length) and (len(self.queue) > 0):
            t_func, t_args = self.queue[self._queue_pointer]
            del self.queue[self._queue_pointer]
            self.jobs.append(myProcess(target=t_func, args=t_args)) 
            self.check_jobs()

        if self.num_running_p < self.num_req_p:
            job2run = self.jobs[self._jobs_pointer]
            if (not job2run.is_alive()) and (job2run._popen == None):
                if verbosity >= 1: 
                    print(f"[INFO] start job-{self._pointer}")
                job2run.start()
                if verbosity >= 2:
                    self._print_job_info()
            elif job2run._popen != None: 
                if verbosity >= 1:
                    print(f"[INFO] job-{self._pointer} is finished.")
                    if verbosity >= 2:
                        self._print_job_info()
            self._pointer += 1
            self._jobs_pointer += 1
        else:
            if verbosity >= 3:
                print(f"[INFO] number of running jobs: {self.num_running_p}.")
    
    def join_all(self):
        """Run join on all processes"""
        for proc in self.jobs:
            proc.join()
    
    def clear_jobs(self):
        """Clear all jobs"""
        self.num_running_p = 0
        self.jobs = []
        self._pointer = None
        self._jobs_pointer = None
        self._queue_pointer = None
        self.queue = deque()

    def set_pointer(self, i: int):
        """Manually set the pointer

        Parameters
        ----------
        i : int
            the new pointer
        """
        self._pointer = i

    def __str__(self):
        info = f"#requested processed: {self.num_req_p}"
        info += f"\n#jobs: {len(self.jobs)}"
        info += f"\n#queued: {len(self.queue)}"
        return info
    
    def _print_job_info(self, text_color=bc.green):
        """Print some info about the job"""
        self.check_jobs()
        print(20*"=")
        cprint("[INFO]", text_color, f"#finished jobs: {self.num_finished_p}")
        cprint("[INFO]", text_color, f"#running jobs: {self.num_running_p}")
        cprint("[INFO]", text_color, f"#remained jobs: {self.num_remain_p}")
        cprint("[INFO]", text_color, f"#queued jobs: {len(self.queue)}")
        print(20*"=")
    
    def _print_exceptions(self):
        """Print list of exceptions raised during run"""
        print(10*"=")
        print("List of exceptions")
        for i, proc in enumerate(self.jobs):
            if proc.exception:
                print(i, proc.exception)
        print(10*"=")
