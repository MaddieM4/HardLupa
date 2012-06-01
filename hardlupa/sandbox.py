import multiprocessing
from runtime import HardRuntime

class Sandbox(object):
    # An isolated process that handles a pool of runtimes.
    def __init__(self):
        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        self.process = multiprocessing.Process(
            target=self.run,
            args=(
				self.child_conn,
			),
		)
        self.process.daemon = True
        self.process.start()

    def run(self):
        self.runtimes = {}
        self.closed = False
        while not self.closed:
            call, args, kwargs = self.recv()
            getattr(self, "_"+call)(*args, **kwargs)

    def send(self, call):
        if self.process.is_alive():
            self.parent_conn.send(call)
        else:
            raise IOError("Process is dead.")

    def recv(self, timeout=0):
        if self.process.is_alive():
            return self.parent_conn.recv()
        else:
            raise IOError("Process is dead.")

    def call(self, name, args, kwargs, timeout=0):
        self.send((call, args, kwargs))
        return self.recv()

    def _create_runtime(self, name=None):
        # Create and return a handle to a runtime
        if (name==None):
            name = "auto_"+str(len(self.runtimes))
        self.runtimes[name] = HardRuntime()

    def _close(self):
        self.closed = True

    def create_runtime(self, **kwargs):
        self.call("create_runtime", (), kwargs)

    def close(self):
        self.call("close", (), {})


