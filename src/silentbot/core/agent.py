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
        
        # 2. Build System Prompt
        system_prompt = (
            "You are SilentBot AGENT (v2027). "
            "Tools: [TOOL: calculate | 2+2], [TOOL: system_info], [TOOL: get_time], [TOOL: web_search | query]."
        )
        
        if self.mode == "normal":
            system_prompt += " IMPORTANT: DO NOT write code. Refuse politely if asked."
        
        if knowledge_hits:
            skills = [f"{k['key']}: {k['expert_prompt']}" for k in knowledge_hits]
            system_prompt += "\nEXPERT MODULES ACTIVE:\n" + "\n".join(skills)

        if memory_hits:
            system_prompt += "\nUSER MEMORY:\n" + "\n".join([f"- {m}" for m in memory_hits])

        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_query}]
        
        # 3. ReAct Loop
        for i in range(3):
            res = call_ai(messages, mode=self.mode)
            content = res["content"]
            m = re.search(r"[TOOL: (\w+)(?: \| (.*?))?]", content)
            if m:
                obs = tools.execute(m.group(1), m.group(2) or "")
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "system", "content": f"OBSERVATION: {obs}"})
            else:
                return {"response": content, "model": res["model"], "tokens": res["tokens_used"]}
        return {"response": content, "model": "limit", "tokens": 0}