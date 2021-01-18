#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime
import multiprocessing as mp
import socket
import traceback

class Process(mp.Process):
    """Process and handle exceptions
    CREDIT: https://stackoverflow.com/a/33599967

    Example (from the same link above):

    def target():
        raise ValueError('Something went wrong...')
    
    p = Process(target = target)
    p.start()
    p.join()
    
    if p.exception:
        error, traceback = p.exception
        print(traceback)
    """
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still rise this exception if you need to

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


# ------------------- bc --------------------
class bc:
    lgrey = '\033[1;90m'
    grey = '\033[90m'           # broing information
    yellow = '\033[93m'         # FYI
    orange = '\033[0;33m'       # Warning

    lred = '\033[1;31m'         # there is smoke
    red = '\033[91m'            # fire!
    dred = '\033[2;31m'         # Everything is on fire

    lblue = '\033[1;34m'
    blue = '\033[94m'
    dblue = '\033[2;34m'

    lgreen = '\033[1;32m'       # all is normal
    green = '\033[92m'          # something else
    dgreen = '\033[2;32m'       # even more interesting

    lmagenta = '\033[1;35m'
    magenta = '\033[95m'        # for title
    dmagenta = '\033[2;35m'

    cyan = '\033[96m'           # system time
    white = '\033[97m'          # final time

    black = '\033[0;30m'

    end = '\033[0m'
    bold = '\033[1m'
    under = '\033[4m'

# ------------------- get_time --------------------
def get_time():
    time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    return time

# ------------------- cprint --------------------
def cprint(type_info, bc_color, text):
    """
    simple print function used for colored logging
    """
    ho_nam = socket.gethostname().split('.')[0]

    print(bc.green          + get_time() + bc.end,
          bc.magenta        + ho_nam     + bc.end,
          bc.bold + bc.grey + type_info  + bc.end,
          bc_color          + text       + bc.end)