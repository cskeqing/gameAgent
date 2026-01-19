from loguru import logger
import json
from src.brain.llm import LLMBrain

class Task:
    def __init__(self, description, status="pending"):
        self.description = description
        self.status = status  # pending, in_progress, completed, failed

    def to_dict(self):
        return {"description": self.description, "status": self.status}

class Planner:
    def __init__(self, llm: LLMBrain):
        self.llm = llm
        self.current_goal = None
        self.plan = []  # List of Task objects
        self.current_task_index = 0

    def set_goal(self, goal):
        self.current_goal = goal
        self.plan = []
        self.current_task_index = 0
        logger.info(f"New goal set: {goal}")
        self._generate_plan()

    def _generate_plan(self):
        """
        Ask LLM to decompose the goal into steps.
        """
        system_prompt = """
        You are a Game AI Planner. 
        Decompose the user's goal into a sequential list of simple tasks.
        Return ONLY a JSON list of strings, for example:
        ["Teleport to Main City", "Walk to NPC", "Talk to NPC", "Accept Quest"]
        Do not add any other text.
        """
        
        try:
            response = self.llm.think(system_prompt, f"Goal: {self.current_goal}")
            # Clean up response (remove markdown code blocks if any)
            response = response.replace("```json", "").replace("```", "").strip()
            
            steps = json.loads(response)
            if isinstance(steps, list):
                self.plan = [Task(step) for step in steps]
                logger.info(f"Plan generated with {len(self.plan)} steps.")
            else:
                logger.error("LLM returned invalid plan format (not a list).")
        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            # Fallback: single step
            self.plan = [Task(self.current_goal)]

    def get_current_task(self):
        if 0 <= self.current_task_index < len(self.plan):
            return self.plan[self.current_task_index]
        return None

    def complete_current_task(self):
        task = self.get_current_task()
        if task:
            task.status = "completed"
            logger.info(f"Task completed: {task.description}")
            self.current_task_index += 1
            
    def get_plan_status(self):
        return [t.to_dict() for t in self.plan]
