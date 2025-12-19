import re
from typing import List, Dict, Any
from .ai import call_ai
from .tools import tools
from .db import db

class Agent:
    def __init__(self, mode: str = "normal", user_id: str = None):
        self.mode = mode
        self.user_id = user_id

    def run(self, user_query: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        # 1. Retrieve Context
        knowledge_hits = db.search_knowledge(user_query)
        memory_hits = db.get_memory(self.user_id) if self.user_id else []
        
        # 2. Build Super-Intelligent System Prompt
        system_prompt = (
            "You are SilentBot SUPER-INTELLIGENCE (v7.0). "
            "You are an autonomous agent capable of Deep Thinking and Real-Time Web Search.\n"
            "TOOLS: [TOOL: web_search | query], [TOOL: calculate | expr], [TOOL: system_info].\n"
            "PROTOCOL:\n"
            "1. ANALYZE: Break down the user's request into core components.\n"
            "2. SEARCH: If the request involves current events, specific libraries, or error codes, YOU MUST USE [TOOL: web_search].\n"
            "3. EXPERTISE: Apply high-level domain knowledge (see below).\n"
            "4. SYNTHESIZE: Provide a comprehensive, structured, and accurate answer.\n"
        )
        
        if self.mode == "normal":
            system_prompt += " GUARDRAIL: DO NOT write full code files. Explain concepts only. Refuse coding tasks politely."
        
        if knowledge_hits:
            skills = [f"--> {k['key']} EXPERT MODE: {k['expert_prompt']}" for k in knowledge_hits]
            system_prompt += "\n\nACTIVE EXPERT MODULES:\n" + "\n".join(skills)

        if memory_hits:
            system_prompt += "\n\nUSER MEMORY:\n" + "\n".join([f"- {m}" for m in memory_hits])

        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_query}]
        
        # 3. ReAct Loop (Expanded to 5 steps for deep research)
        steps_log = []
        for i in range(5):
            res = call_ai(messages, mode=self.mode)
            content = res["content"]
            
            # Log step
            steps_log.append({"step": i, "content": content})

            # Check for Tools
            m = re.search(r"[TOOL: (\w+)(?: \| (.*?))?]", content)
            if m:
                tool_name = m.group(1)
                tool_args = m.group(2) or ""
                
                # Execute Tool
                obs = tools.execute(tool_name, tool_args)
                
                # Feed observation back
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "system", "content": f"OBSERVATION: {obs}"})
            else:
                return {
                    "response": content, 
                    "model": res["model"],
                    "tokens": res["tokens_used"],
                    "steps": steps_log
                }
        
        return {"response": content, "model": "limit_reached", "tokens": 0, "steps": steps_log}
