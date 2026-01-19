import yaml
import os
from loguru import logger

class ConfigManager:
    def __init__(self, config_path="configs/agent_config.yaml"):
        self.config_path = config_path
        self.config = {}
        
        # Ensure config dir exists
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        self.load()

    def load(self):
        if not os.path.exists(self.config_path):
            self._create_default()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info("Config loaded.")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def _create_default(self):
        default_config = {
            "behavior": {
                "risk_level": "conservative",
                "humanization": {
                    "mouse_speed": 0.5,
                    "jitter": True
                }
            },
            "llm": {
                "model": "gpt-4o-mini",
                "api_base": "https://api.openai.com/v1"
            },
            "thresholds": {
                "heal_at_hp": 40
            }
        }
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            self.config = default_config
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")

    def get(self, key, default=None):
        keys = key.split(".")
        val = self.config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default
