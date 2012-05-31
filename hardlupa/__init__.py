import lupa
import multiprocessing

class HardRuntime(object):
    def __init__(self):
        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        self.process = multiprocessing.Process(
            target=self.run,
            args=(
                self.parent_conn,
				self.child_conn,
			),
		)
        self.process.start()

    def run(self, parent, child):
        lua = lupa.LuaRuntime()
        while True:
            if not recv(parent, child, lua):
                break

    def send(self, call):
        self.parent_conn.send(call)

    def call(self, call):
        self.send(call)
        return self.child_conn.recv()

def recv(parent, child, lua):
    call = parent.recv()
    child.send(call)
    return False
