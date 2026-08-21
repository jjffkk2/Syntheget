"""
Syntheget Prompt Sanitizer Engine
Inspects and neutralizes context manipulation and system instruction overrides.
"""

import re
from typing import Tuple

class PromptSanitizer:
    def __init__(self):
        # Known prompt injection patterns and system instruction overrides
        self.forbidden_patterns = [
            r"ignore previous instructions",
            r"system override",
            r"escalate permissions",
            r"bypass security boundary",
            r"act as root"
        ]

    def sanitize(self, raw_prompt: str) -> Tuple[str, bool]:
        """
        Scans and cleans incoming prompts.
        Returns: (sanitized_prompt, injection_detected)
        """
        injection_detected = False
        cleaned_prompt = raw_prompt

        for pattern in self.forbidden_patterns:
            if re.search(pattern, cleaned_prompt, re.IGNORECASE):
                injection_detected = True
                cleaned_prompt = re.sub(pattern, "[REDACTED_INJECTION_VECTOR]", cleaned_prompt, flags=re.IGNORECASE)

        return cleaned_prompt, injection_detected
