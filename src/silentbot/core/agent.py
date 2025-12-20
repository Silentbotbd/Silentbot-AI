import re
import json
import logging
from typing import List, Dict, Any
from .ai import call_ai
from .tools import tools
from .db import db

logger = logging.getLogger("silentbot.agent")

class Agent:
    def __init__(self, mode: str = "normal", user_id: str = None):
        self.mode = mode
        self.user_id = user_id
        # "Overthinking" limit: How many steps the agent can take
        self.max_steps = 8 if mode == "pro" else 3

    def run(self, user_query: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        The Core Intelligent Loop (ReAct Pattern).
        """
        # 1. Context Retrieval
        knowledge_hits = db.search_knowledge(user_query) if hasattr(db, 'search_knowledge') else []
        memory_hits = db.get_memory(self.user_id) if self.user_id and hasattr(db, 'get_memory') else []
        
        # 2. System Prompt Engineering
        system_prompt = (
            "You are SilentBot V5.2 ULTIMATE. "
            "You are an autonomous, intelligent agent capable of Deep Thinking, Research, and Task Execution.\n"
            "AVAILABLE TOOLS:\n"
            "- [TOOL: web_search | query] -> Search the internet (DuckDuckGo/Google/Bing logic).\n"
            "- [TOOL: scholar_search | query] -> Find academic papers and technical PDFs.\n"
            "- [TOOL: deep_research | query] -> Perform exhaustive multi-angle research.\n"
            "- [TOOL: calculate | expression] -> Math calculations.\n"
            "- [TOOL: system_info] -> Get host details.\n\n"
            "PROTOCOL:\n"
            "1. THOUGHT: Analyze the request. Break it down. Check memories.\n"
            "2. PLAN: If research is needed, use tools. Do NOT guess facts.\n"
            "3. ACTION: Issue a [TOOL: ...] command.\n"
            "4. OBSERVATION: Wait for result.\n"
            "5. SYNTHESIS: Combine all findings into a perfect response.\n"
        )
        
        if self.mode == "normal":
            system_prompt += " NOTE: You are in NORMAL mode. Keep answers concise. Coding capabilities restricted."
        else:
            system_prompt += " NOTE: You are in PRO mode. Use full deep capabilities. Be exhaustive."

        if memory_hits:
            system_prompt += "\n\nUSER MEMORY CONTEXT:\n" + "\n".join([f"- {m}" for m in memory_hits])

        # Prepare message buffer
        messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_query}]
        
        steps_log = []
        final_response = ""
        
        # 3. Execution Loop
        for step_i in range(self.max_steps):
            try:
                # Call AI
                res = call_ai(messages, mode=self.mode)
                content = res["content"]
                
                # Check for Tool Usage
                tool_match = re.search(r"[TOOL: (\w+)(?: \| (.*?))?]", content)
                
                if tool_match:
                    # It's a tool call
                    tool_name = tool_match.group(1)
                    tool_args = tool_match.group(2) or ""
                    
                    log_entry = f"Step {step_i+1}: Using {tool_name}..."
                    steps_log.append({"step": step_i, "content": log_entry, "type": "tool_use"})
                    
                    # Execute
                    obs = tools.execute(tool_name, tool_args)
                    
                    steps_log.append({"step": step_i, "content": f"Observation: {obs[:200]}...", "type": "observation"})

                    # Feed back to AI
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "system", "content": f"OBSERVATION: {obs}"})
                    
                else:
                    # It's the final answer (or a thought without action)
                    # If it looks like a final answer (doesn't ask for tool), we break
                    final_response = content
                    steps_log.append({"step": step_i, "content": "Synthesizing Final Answer", "type": "thought"})
                    break
                    
            except Exception as e:
                logger.error(f"Agent Loop Error: {e}")
                final_response = "I encountered an internal error while thinking. Please try again."
                break
        
        return {
            "response": final_response, 
            "model": "silentbot-v5.2",
            "tokens": 0,
            "steps": steps_log
        }