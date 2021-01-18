<div align="center">
    <br>
    <h2>Parallelize Python codes</h2>
</div>

<p align="center">
    <a href="https://github.com/kasra-hosseini/parhugin/workflows/Continuous%20integration/badge.svg">
        <img alt="Continuous integration badge" src="https://github.com/kasra-hosseini/parhugin/workflows/Continuous%20integration/badge.svg">
    </a>
    <a href="https://github.com/kasra-hosseini/parhugin/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
    <br/>
</p>

`parhugin` provides functions to:

- [run one or more Python functions in parallel using multiprocessing](#run-one-or-more-python-functions-in-parallel-using-multiprocessing)


Table of contents
-----------------

- [Installation and setup](#installation)
- [Run one or more Python functions in parallel using multiprocessing](#run-one-or-more-python-functions-in-parallel-using-multiprocessing)
- [Complete examples](#complete-examples)

## Installation

1. **install using pip**

    ```bash
    pip install git+https://github.com/kasra-hosseini/parhugin.git
    ```

2. **install parhugin from the source code**:

    * Clone parhugin source code:

    ```bash
    git clone https://github.com/kasra-hosseini/parhugin.git 
    ```

    * Install parhugin:

    ```
    cd /path/to/my/parhugin
    python setup.py install
    ```

    Alternatively:

    ```
    cd /path/to/my/parhugin
    pip install -v -e .
    ```

## Run one or more Python functions in parallel using multiprocessing 

In this scenario, we have:

- one or more functions
- a list of jobs to be run in parallel, e.g.: 
```python
[   
    [func1, (arg1_1, arg2_1, arg3_1)],
    [func1, (arg1_2, arg2_2, arg3_2)],  
    [func2, (...)],
    ...
] 
```
⚠️ If a function has only one argument, do not forget to add it to the above list either `[func_one_arg, [arg1]]` or `[func_one_arg, (arg1,)]`.

- User specifies the number of processes to be run in parallel.
- `parhugin` parallelizes by distributing the jobs following FIFO on the requested number of processes.

### Example 1

First, we import `parhugin` and define two simple functions called `func1` and `func2`. These functions can have different number of arguments.

```python
from parhugin import multiFunc
import time

# Define two simple functions, func1 and func2 
# Note that functions can have different number of arguments
def func1(a, b, sleep=0.5, info="func1"): 
    print(f"start, {info} calculated {a+b}")
    time.sleep(sleep)
    print(f"end, {info}")

def func2(a, sleep=0.2, info="func2"): 
    print(f"start, {info} prints {a}")
    time.sleep(sleep)
    print(f"end, {info}")
```

Next, we specify the number of processes to run in parallel. This can be the number of processors if the jobs are CPU-intensive. Otherwise, you can set this to any other values.

```python
myproc = multiFunc(num_req_p=10)
```

Now, we need to add jobs to be run in parallel. There are different ways to do this:

1) Add one function and its arguments:

```python
myproc.add_job(target_func=func1, target_args=(2, 3, 0.5, "func1"))
print(myproc)
```

Similarly, we can add another function:

```python
myproc.add_job(target_func=func2, target_args=(10, 0.2, "func2"))
print(myproc)
```

2) Create a list of jobs:

```python
list_jobs = []
for i in range(1, 20):
    list_jobs.append([func2, (f"{i}", 0.2, "func2")])

# and then adding them to myproc
myproc.add_list_jobs(list_jobs)
print(myproc)
```

Finally, run the jobs on the requested number of processes:

```python
myproc.run_jobs()
```

It is also possible to change the verbosity level of the output by:

```python
myproc.run_jobs(verbosity=2)
```

## Complete examples

### Example 1

```python
from parhugin import multiFunc
import time

# Define two simple functions, func1 and func2 
# Note that functions can have different number of arguments
def func1(a, b, sleep=0.5, info="func1"): 
    print(f"start, {info} calculated {a+b}")
    time.sleep(sleep)
    print(f"end, {info}")

def func2(a, sleep=0.2, info="func2"): 
    print(f"start, {info} prints {a}")
    time.sleep(sleep)
    print(f"end, {info}")

myproc = multiFunc(num_req_p=10)
myproc.add_job(target_func=func1, target_args=(2, 3, 0.5, "func1"))
print(myproc)

myproc.add_job(target_func=func2, target_args=(10, 0.2, "func2"))
print(myproc)

list_jobs = []
for i in range(1, 20):
    list_jobs.append([func2, (f"{i}", 0.2, "func2")])

# and then adding them to myproc
myproc.add_list_jobs(list_jobs)
print(myproc)

myproc.run_jobs(verbosity=2)
```
