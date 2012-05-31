import lupa
import multiprocessing

safe_lua_modules = [
    "table",
    "string",
    "math",
    "collectgarbage",
]

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
        globalflush(lua)
        globs = lua.globals()
        while True:
            try:
                result = recv(conn, lua, globs)
                if type(result) == tuple:
                    if result[0] == "globals_update":
                        globs = result[1]
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

# Receive a request in the remote process
def recv(conn, lua, globs):
    action, details = conn.recv()
    if not isinstance(details, basestring):
        raise TypeError("Action details should be a string. Got %r" % details)
    if action=="eval":
        conn.send(lua.eval(details))
    elif action=="exec":
        conn.send(lua.execute(details))
    elif action=="globals_update":
        globalflush(lua, details[1], details[2])
        return ("globals_update", lua.globals())
    else:
        raise ValueError("Unknown action type %r" % action)

# Save and/or restore the state of the globals in the Lupa interpreter
def globalflush(lua, names=safe_lua_modules, values={}):
    lua_globals = lua.globals()
    if not values:
        for x in lua_globals:
            values[x] = lua_globals[x]

    for x in lua_globals:
        if x in values:
            lua_globals[x] = values[x]
        else:
            lua_globals[x] = None
