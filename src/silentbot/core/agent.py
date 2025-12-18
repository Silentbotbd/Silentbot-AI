import re
from typing import List, Dict, Any
from .ai import call_ai
from .tools import tools

class Agent:
    def __init__(self, mode: str = "normal"):
        self.mode = mode

    def run(self, user_query: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        system_prompt = (
            "You are SilentBot AGENT. "
            "Tools: [TOOL: calculate | 2+2], [TOOL: system_info], [TOOL: get_time], [TOOL: web_search | query]."
        )
        if self.mode == "normal":
            system_prompt += " IMPORTANT: DO NOT write code. Refuse politely if asked."

        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_query}]
        
        for i in range(3):
            res = call_ai(messages, mode=self.mode)
            content = res["content"]
            m = re.search(r"\[TOOL: (\w+)(?: \| (.*?))?\]", content)
            if m:
                obs = tools.execute(m.group(1), m.group(2) or "")
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "system", "content": f"OBSERVATION: {obs}"})
            else:
                return {"response": content, "model": res["model"], "tokens": res["tokens_used"]}
        return {"response": content, "model": "limit", "tokens": 0}
