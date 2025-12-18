import os, platform, datetime, math
class ToolRegistry:
    def __init__(self): self.tools = {"system_info": self.sys, "calculate": self.calc, "get_time": self.time}
    def sys(self, a): return f"{platform.system()} {platform.release()}"
    def time(self, a): return str(datetime.datetime.now())
    def calc(self, e):
        try: return str(eval(e, {"__builtins__":{}}, {"abs":abs,"round":round,"math":math}))
        except: return "Error"
    def execute(self, n, a): return self.tools.get(n, lambda x: "Not found")(a)
tools = ToolRegistry()
