import logging
from fabric import io

OutputLooper = io.OutputLooper

class RoroliteOutputLooper(OutputLooper):
    """Replacement to OutputLooper of Fabric that doesn't print prefix
    in the output.
    """
    def __init__(self, *args, **kwargs):
        OutputLooper.__init__(self, *args, **kwargs)
        self.prefix = ""

def hijack_output_loop():
    """Hijacks the fabric's output loop to supress the '[hostname] out:'
    prefix from output.
    """
    io.OutputLooper = RoroliteOutputLooper

def setup_logger(verbose=False):
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(format='[%(name)s] %(message)s', level=level)
