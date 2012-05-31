import lupa
import multiprocessing

class HardRuntime(object):
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

    def run(self, conn):
        lua = lupa.LuaRuntime()
        while True:
            try:
                recv(conn, lua)
            except Exception as e:
                conn.send(e)
        print "HardRuntime sandbox is exiting..."

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

    def call(self, call, timeout=0):
        self.send(call)
        return self.recv()

    # Evaluate an expression
    def eval(self, code, timeout=0):
        return self.call(("eval", code), timeout)

    # Execute some code
    def execute(self, code, timeout=0):
        return self.call(("exec", code), timeout)

    # Get all the globals in the interpreter
    def globals(self, timeout=0):
        return self.call(("globals", ""), timeout=0)

# Receive a request in the remote process
def recv(conn, lua):
    action, details = conn.recv()
    if not isinstance(details, basestring):
        raise TypeError("Action details should be a string. Got %r" % details)
    if action=="eval":
        conn.send(lua.eval(details))
    elif action=="exec":
        conn.send(lua.execute(details))
    elif action=="globals":
        conn.send(list(lua.globals().keys()))
    else:
        raise ValueError("Unknown action type %r" % action)
