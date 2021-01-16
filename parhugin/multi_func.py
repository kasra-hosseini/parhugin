#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "Kasra Hosseini"
__license__ = "MIT License"

import multiprocessing
import time
from typing import Union, Sequence
from .utils import Process as myProcess

class multiFunc:

    def __init__(self, num_req_p: Union[int, None]=None, 
                 sleep_time: float=0.1):
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
        self.jobs = []
        self._pointer = None
    
    def add_job(self, target_func, target_args: Sequence):
        """Add a job to the list of jobs

        Parameters
        ----------
        target_func
            Serial version of the function to be parallelized
        target_args : Sequence
            Arguments of the function (serial version)
        """
        p = myProcess(target=target_func, args=target_args)
        self.jobs.append(p)

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
        """Check th number of running/finished/remained jobs"""
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
    
    def run_jobs_index(self, i1: int, i2: int):
        """Run jobs from i1 to i2 indices

        Parameters
        ----------
        i1 : int
            index 1
        i2 : int
            index 2
        """
        assert (i2 > i1 >= 0), f"{i2} should be larger than {i1} and {i1} should be >= 0"
        assert (i2 <= len(self.jobs)), f"{i2} is more than the number of jobs ({len(self.jobs)})"

        self._pointer = i1
        self.job_start_time = time.time() 
        while self._pointer < i2:
            self.start_job()
            time.sleep(self.sleep_time)
        self.join_all()

        self._print_job_info()
        self.job_elapsed_time = time.time() - self.job_start_time
        print(f"Total time: {self.job_elapsed_time}")
        self._print_exceptions()

    def run_jobs(self):
        """Run all the jobs"""
        self.run_jobs_index(0, len(self.jobs))
    
    def start_job(self, verbose: bool=False):
        """Start a process after checking:
           1. number of running processes is less than the number of requested processes
           2. the requested process is not alive or has not been done before

        Parameters
        ----------
        verbose : bool, optional
            verbosity, by default False
        """
        self.check_jobs()
        if self.num_running_p < self.num_req_p:
            job2run = self.jobs[self._pointer]
            if (not job2run.is_alive()) and (job2run._popen == None):
                print(f"[INFO] start job-{self._pointer}")
                job2run.start()
            elif job2run._popen != None: 
                print(f"[INFO] job-{self._pointer} is finished.")
            self._pointer += 1
        else:
            if verbose:
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
        return info
    
    def _print_job_info(self):
        """Print some info about the job"""
        self.check_jobs()
        print(10*"=")
        print(f"#finished jobs: {self.num_finished_p}")
        print(f"#running jobs: {self.num_running_p}")
        print(f"#remained jobs: {self.num_remain_p}")
        print(10*"=")
    
    def _print_exceptions(self):
        """Print list of exceptions raised during run"""
        print(10*"=")
        print("List of exceptions")
        for i, proc in enumerate(self.jobs):
            if proc.exception:
                print(i, proc.exception)
        print(10*"=")
