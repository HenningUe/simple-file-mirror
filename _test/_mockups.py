
import os

from . import _setup


class _TestLogger(object):
    LOGFILE = "test.log"

    def __init__(self):
        self.logfilepath = os.path.join(_setup.TEST_ROOT, self.LOGFILE)
        if not os.path.isdir(_setup.TEST_ROOT):
            os.makedirs(_setup.TEST_ROOT)
        if os.path.isfile(self.logfilepath):
            os.remove(self.logfilepath)

    def free_message(self, msg):
        self._do_log(msg)

    def info(self, msg, *args, **kwargs):
        self._do_log("INFO: " + msg)

    def mail(self, msg, *args, **kwargs):
        self._do_log("MAIL: " + msg)

    def verbose(self, msg, *args, **kwargs):
        self._do_log("VERBOSE: " + msg)

    def warn(self, msg, *args, **kwargs):
        self._do_log("WARN: " + msg)

    def error(self, msg, *args, **kwargs):
        self._do_log("ERROR: " + msg)

    def exception(self, msg, *args, **kwargs):
        self._do_log("EXCEPTION: " + msg)

    def _do_log(self, msg):
        print(msg)
        with open(self.logfilepath, 'a+') as f:
            f.write(msg + "\n")
