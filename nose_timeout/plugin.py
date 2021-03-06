import logging
import signal


from nose.plugins.base import Plugin


logger = logging.getLogger('nose.plugins.nose_timeout')


class TimeoutException(Exception):
    message = "Stopped by timeout"


class NoseTimeout(Plugin):
    """
    Abort long-running tests
    """
    name = 'timeout'

    def __init__(self):
        Plugin.__init__(self)
        self.timeout = 0

    def options(self, parser, env):
        parser.add_option(
            "--timeout",
            action="store",
            dest="timeout",
            default=env.get('NOSE_TIMEOUT', 0),
            help=(
                "When reach this timeout the test is aborted"
            ),
        )

    def configure(self, options, config):
        self.timeout = options.timeout
        if not self._options_are_valid():
            self.enabled = False
            return

        self.enabled = True

    def _options_are_valid(self):
        try:
            self.timeout = int(self.timeout)
        except ValueError:
            logger.critical("--timeout must be an integer")
            return False

        self.timeout = int(self.timeout)
        if self.timeout < 0:
            logger.critical("--timeout must be greater or equal than 0")
            return False
        return True

    def prepareTestCase(self, test):
        if self.timeout:
            def timeout(result):
                def __handler(signum, frame):
                    msg = "Function execution is longer than %s second(s). Aborted." % self.timeout
                    raise TimeoutException(msg)

                sig_handler = signal.signal(signal.SIGALRM, __handler)
                signal.alarm(self.timeout)
                try:
                    test.test(result)
                except TimeoutException as e:
                    print(e.message + " timeout")
                finally:
                    signal.signal(signal.SIGALRM, sig_handler)
                    signal.alarm(0)
            return timeout
