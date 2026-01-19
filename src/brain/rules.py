from loguru import logger

class RuleEngine:
    def __init__(self):
        self.rules = []

    def load_rules(self, rules_data):
        """
        Load rules list.
        rules_data: list of dicts. 
        Example: [{"trigger": {"hp": "< 30"}, "action": "press_r"}]
        """
        self.rules = rules_data
        logger.info(f"Loaded {len(self.rules)} rules.")

    def evaluate(self, state):
        """
        Evaluate current state against rules.
        state: dict (flat key-value pairs preferred)
        Returns: action_name (str) or None
        """
        for rule in self.rules:
            trigger = rule.get("trigger", {})
            if self._check_condition(trigger, state):
                return rule.get("action")
        return None

    def _check_condition(self, trigger, state):
        # Trigger is a dict of requirements: {"hp": "< 50", "combat": "== True"}
        try:
            for key, condition in trigger.items():
                if key not in state:
                    # Key missing in state means we can't evaluate -> False
                    return False
                
                val = state[key]
                
                # Simple parsing of operator
                # Supported: "<", ">", "==", "!=", "<=", ">="
                # Condition string format: "OP VALUE" e.g. "< 50"
                parts = str(condition).split(" ")
                if len(parts) == 2 and parts[0] in ["<", ">", "<=", ">=", "==", "!="]:
                    op, target = parts[0], parts[1]
                else:
                    # Assume equality if no operator or boolean/string
                    if isinstance(condition, bool):
                        if val != condition: return False
                        continue
                    # String match
                    if str(val) != str(condition): return False
                    continue

                # Cast target to float if possible
                try:
                    target = float(target)
                    val = float(val)
                except:
                    # String comparison if not numbers
                    target = str(target)
                    val = str(val)

                if op == "<" and not (val < target): return False
                if op == ">" and not (val > target): return False
                if op == "<=" and not (val <= target): return False
                if op == ">=" and not (val >= target): return False
                if op == "==" and not (val == target): return False
                if op == "!=" and not (val != target): return False
                
            return True
        except Exception as e:
            logger.error(f"Rule evaluation error: {e}")
            return False
