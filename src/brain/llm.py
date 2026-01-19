from litellm import completion
from loguru import logger
import os
import json

class LLMBrain:
    def __init__(self, model="gpt-4o-mini", api_base=None, api_key=None):
        self.model = model
        self.api_base = api_base
        self.api_key = api_key

    def set_model(self, model_name):
        self.model = model_name

    def think(self, system_prompt, user_content):
        """
        Call LLM to make a decision.
        user_content: str or list (for multimodal inputs)
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        try:
            # Check for API Key presence if strictly needed
            if not self.api_key and "gpt" in self.model and not os.environ.get("OPENAI_API_KEY"):
                logger.warning("No OpenAI API Key found. Switching to MOCK mode for demo.")
                return self._mock_response(user_content)

            logger.debug(f"LLM Thinking with model {self.model}...")
            
            kwargs = {"model": self.model, "messages": messages}
            if self.api_base:
                kwargs["api_base"] = self.api_base
            if self.api_key:
                kwargs["api_key"] = self.api_key

            response = completion(**kwargs)
            content = response.choices[0].message.content
            logger.debug(f"LLM Response: {content}")
            return content
        except Exception as e:
            logger.error(f"LLM think failed: {e}")
            return self._mock_response(user_content)

    def decide_action(self, task, vision_data):
        """
        Specific method for Auto-Pilot to determine next physical action.
        vision_data: dict containing 'objects' and 'texts'
        """
        system_prompt = """
        You are a GUI Automation Agent.
        Based on the Current Task and the Vision Data (list of detected objects and text on screen),
        output the next physical action in JSON format.
        
        Vision Data Format:
        - texts: list of {text, box: [x1,y1,x2,y2]}
        - objects: list of {name, box: [x1,y1,x2,y2]}

        Output JSON Format:
        {
            "action": "click" | "type" | "press" | "wait" | "finish",
            "target": "text string to find" | [x, y] coordinates | null,
            "value": "text to type" | "key name" | null,
            "reasoning": "short explanation"
        }
        
        Example 1:
        Task: "Open Chrome"
        Vision: texts=[{"text": "Google Chrome", "box": [10, 10, 50, 50]}]
        Output: {"action": "click", "target": "Google Chrome", "value": null, "reasoning": "Found Chrome icon text"}

        Example 2:
        Task: "Type 'hello'"
        Vision: ...
        Output: {"action": "type", "target": null, "value": "hello", "reasoning": "Typing text"}

        Example 3:
        Task: "Search for weather"
        Vision: texts=[{"text": "Search", "box": [100, 100, 200, 120]}]
        Output: {"action": "click", "target": "Search", "value": null, "reasoning": "Clicking search bar"}
        """
        
        user_content = json.dumps({
            "current_task": task,
            "vision_data": vision_data
        }, ensure_ascii=False)
        
        response = self.think(system_prompt, user_content)
        try:
            # Clean response
            response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Failed to parse action JSON: {e}")
            return {"action": "wait", "reasoning": "Parse error"}

    def _mock_response(self, user_input):
        logger.info("Generating MOCK response...")
        if "Goal:" in str(user_input):
            goal = str(user_input).replace("Goal:", "").strip()
            return json.dumps([
                f"Open Application for '{goal}'",
                "Locate Search Bar",
                f"Type '{goal}'",
                "Press Enter",
                "Wait for Results",
                "Verify Success"
            ])
        
        # Mock Decision Response
        return json.dumps({
            "action": "wait", 
            "target": None, 
            "value": None, 
            "reasoning": "Mock mode: Waiting..."
        })
