from litellm import completion
from loguru import logger
import os

class LLMBrain:
    def __init__(self, model="gpt-4o-mini"):
        # Default to a cost-effective model
        self.model = model

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
            logger.debug(f"LLM Thinking with model {self.model}...")
            response = completion(model=self.model, messages=messages)
            content = response.choices[0].message.content
            logger.debug(f"LLM Response: {content}")
            return content
        except Exception as e:
            logger.error(f"LLM think failed: {e}")
            return "Error: " + str(e)
