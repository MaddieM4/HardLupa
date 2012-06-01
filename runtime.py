import lupa

safe_lua_modules = [
    "coroutine",
    "assert",
    "tostring",
    "tonumber",
    "print",
    "module",
    "bit",
    "package",
    "error",
    "debug",
    "rawequal",
    "unpack",
    "pairs",
    "table",
    "next",
    "math",
    "_G",
    "_VERSION",
    "string",
    "type",
    "collectgarbage",
]

class HardRuntime(object):
    def __init__(self):
        self.lua = lupa.LuaRuntime()
        self.globalflush()

    # Evaluate an expression
    def eval(self, code):
        return self.lua.eval(code)

    # Execute some code
    def execute(self, code):
        return self.lua.execute(code)

    # Get all the global names in the interpreter
    def globals(self):
        return list(self.lua.globals().keys())

    def globalflush(self, **kwargs):
        return globalflush(self.lua, **kwargs)

# Shrink and/or restore the state of the globals in the Lupa interpreter
def globalflush(lua, names=safe_lua_modules, values={}):
    lua_globals = lua.globals()
    if not len(values):
        for x in names:
            values[x] = lua_globals[x]

    for x in lua_globals:
        if x in values:
            lua_globals[x] = values[x]
        else:
            #print "Deleting ", repr(x)
            lua_globals[x] = None

