#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest
from parallel_lib import multiFunc
import time

def mysum(a, b, sleep=0.5, info="mysum"): 
    print(f"start {info}")
    print(f"{info} calculated {a+b}")
    time.sleep(sleep)
    print(f"end {info}")

def test_multiFunc():
    myproc = multiFunc(10)
    assert myproc.num_req_p == 10

    myproc.add_job(target_func=mysum, target_args=(2, 3, 0.5, "1"))
    assert len(myproc.jobs) == 1

    list_jobs = []
    for i in range(1, 20):
        list_jobs.append([mysum, (4, 5, 0.5, f"{i}")])
    
    myproc.add_list_jobs(list_jobs)
    assert len(myproc.jobs) == 20 
    
    myproc.check_jobs()
    assert myproc.num_running_p == 0
    assert myproc.num_remain_p == 20
    assert myproc.num_finished_p == 0

    myproc.run_jobs()
    assert myproc.num_running_p == 0
    assert myproc.num_remain_p == 0
    assert myproc.num_finished_p == 20