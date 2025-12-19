import os
import platform
import datetime
import math
import json
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger("silentbot.tools")

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "system_info": self.sys, 
            "calculate": self.calc, 
            "get_time": self.time,
            "web_search": self.web_search_smart,
            "scholar_search": self.scholar_search,
            "deep_research": self.deep_research_task
        }

    def sys(self, a): 
        return f"OS: {platform.system()} {platform.release()} | Ver: {platform.version()} | Machine: {platform.machine()}"

    def time(self, a): 
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def calc(self, e):
        try: 
            # Safe(r) eval
            return str(eval(e, {"__builtins__":{}}, {"abs":abs,"round":round,"math":math,"pow":math.pow,"sqrt":math.sqrt,"max":max,"min":min}))
        except Exception as err: 
            return f"Math Error: {err}"

    def web_search_smart(self, query):
        """
        Intelligent Web Search using DuckDuckGo.
        Supports standard queries.
        """
        logger.info(f"Executing Smart Search: {query}")
        try:
            results = DDGS().text(query, max_results=6)
            if not results:
                return "No matching results found on the web."
            
            summary = [f"--- Search Results for '{query}' ---"]
            for i, r in enumerate(results):
                summary.append(f"{i+1}. [{r['title']}]({r['href']})\n   {r['body']}")
            return "\n".join(summary)
        except Exception as e:
            return f"Search Engine Connection Error: {str(e)}"

    def scholar_search(self, query):
        """
        Simulated Scholar Search (using specific academic keywords with DDG)
        """
        logger.info(f"Executing Scholar Search: {query}")
        academic_query = f"{query} site:edu OR site:org OR filetype:pdf"
        return self.web_search_smart(academic_query)

    def deep_research_task(self, query):
        """
        Performs a multi-step 'Deep Search' by aggregating varied queries.
        """
        logger.info(f"Executing Deep Research: {query}")
        
        # 1. General Search
        general = self.web_search_smart(query)
        
        # 2. News/Recent Search (Simulated by adding 'latest')
        news = self.web_search_smart(f"latest news {query}")
        
        return f"=== GENERAL KNOWLEDGE ===\n{general}\n\n=== LATEST DEVELOPMENTS ===\n{news}"

    def execute(self, tool_name, args):
        func = self.tools.get(tool_name)
        if not func:
            return f"Error: Tool '{tool_name}' not found."
        try:
            return func(args)
        except Exception as e:
            return f"Error executing {tool_name}: {e}"

tools = ToolRegistry()
