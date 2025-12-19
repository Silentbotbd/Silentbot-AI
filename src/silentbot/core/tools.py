import os
import platform
import datetime
import math
import json
from duckduckgo_search import DDGS

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "system_info": self.sys, 
            "calculate": self.calc, 
            "get_time": self.time,
            "web_search": self.web_search_real
        }

    def sys(self, a): 
        return f"OS: {platform.system()} {platform.release()} | Ver: {platform.version()}"

    def time(self, a): 
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def calc(self, e):
        try: 
            return str(eval(e, {"__builtins__":{}}, {"abs":abs,"round":round,"math":math,"pow":math.pow,"sqrt":math.sqrt}))
        except Exception as err: 
            return f"Math Error: {err}"

    def web_search_real(self, query):
        """Performs a real deep web search using DuckDuckGo."""
        print(f"[DEBUG] Searching Web for: {query}")
        try:
            results = DDGS().text(query, max_results=5)
            if not results:
                return "No results found."
            
            # Format results for the AI
            summary = []
            for r in results:
                summary.append(f"- [{r['title']}]({r['href']}): {r['body']}")
            return "\n".join(summary)
        except Exception as e:
            return f"Search Error: {str(e)}"

    def execute(self, n, a): 
        return self.tools.get(n, lambda x: "Tool not found")(a)

tools = ToolRegistry()