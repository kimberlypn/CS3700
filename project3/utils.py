import sys
import datetime
import time


def current_time():
    """Returns the current time in seconds"""
    return time.time()


def log(string):
    """Logs a message with a timestamp"""
    sys.stderr.write("{timestamp} {msg}\n".format(
        timestamp=datetime.datetime.now().strftime("%H:%M:%S.%f"),
        msg=string
    ))


def wrap_sequence(sequence, data=None):
    """Sequence number is a 32 bit number, which wraps back to 0 at 2^32"""
    data_length = len(data) if data is not None else 0
    return (sequence + data_length) % (2**32 - 1)
