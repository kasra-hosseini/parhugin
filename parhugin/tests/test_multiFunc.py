#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest
from parhugin import multiFunc
import time

def mysum(a, b, sleep=0.5, info="mysum"): 
    print(f"start {info}")
    print(f"{info} calculated {a+b}")
    time.sleep(sleep)
    print(f"end {info}")

def mydivide(a, b):
    return a/b

def test_multiFunc():
    myproc = multiFunc(10)
    assert myproc.num_req_p == 10

    # add one job
    myproc.add_job(target_func=mysum, target_args=(2, 3, 0.1, "1"))
    assert len(myproc.queue) == 1

    # add a list of jobs
    list_jobs = []
    for i in range(1, 20):
        list_jobs.append([mysum, (4, 5, 0.01, f"{i}")])
    
    myproc.add_list_jobs(list_jobs)
    assert len(myproc.queue) == 20 
    
    myproc.check_jobs()
    assert myproc.num_running_p == 0
    assert myproc.num_remain_p == 0
    assert myproc.num_finished_p == 0
    assert myproc.num_exceptions_p == 0
    assert len(myproc.queue) == 20 

    myproc.run_jobs()
    assert myproc.num_running_p == 0
    assert myproc.num_remain_p == 0
    assert myproc.num_finished_p == 20
    assert myproc.num_exceptions_p == 0

def test_multiFunc_exception():
    myproc = multiFunc(5)
    assert myproc.num_req_p == 5

    # --- add jobs
    list_jobs = []
    for i in range(1, 5):
        list_jobs.append([mydivide, (i, i+1)])
    # add a faulty job
    list_jobs.append([mydivide, (10, 0)])
    # continue adding jobs
    for i in range(5, 10):
        list_jobs.append([mydivide, (i, i+1)])

    myproc.add_list_jobs(list_jobs)
    assert len(myproc.queue) == 10

    myproc.run_jobs()

    myproc.check_jobs()
    assert myproc.num_running_p == 0
    assert myproc.num_remain_p == 0
    assert myproc.num_finished_p == 10
    assert myproc.num_exceptions_p == 1

