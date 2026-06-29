import json
import os
from typing import Any, Dict, List
from utils.logger import logger

DEFAULT_PROFILE = {
    "target_role": "Software Engineer",
    "experience_level": "Mid Level",
    "skills": [],
    "resume_raw": "",
    "resume_score": 0,
    "resume_analysis": {
        "strengths": [],
        "weaknesses": [],
        "suggestions": []
    },
    "skill_gap": {
        "match_percentage": 0,
        "matching_skills": [],
        "missing_skills": []
    },
    "roadmap": [],
    "interview_session": {
        "active": False,
        "current_question_index": -1,
        "questions": [],
        "answers": [],
        "feedback": []
    },
    "chat_history": []
}

class ProfileMemory:
    """Manages local JSON persistence for user career profile and progress."""
    
    def __init__(self, file_path: str = "profile_store.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            self.save_profile(DEFAULT_PROFILE)

    def load_profile(self) -> Dict[str, Any]:
        """Loads user profile from disk."""
        try:
            if not os.path.exists(self.file_path):
                return DEFAULT_PROFILE.copy()
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Fill missing keys to ensure backward compatibility
                profile = DEFAULT_PROFILE.copy()
                profile.update(data)
                return profile
        except Exception as e:
            logger.error(f"Failed to load profile memory: {e}")
            return DEFAULT_PROFILE.copy()

    def save_profile(self, profile: Dict[str, Any]) -> bool:
        """Saves user profile to disk."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save profile memory: {e}")
            return False

    def update_field(self, field: str, value: Any) -> bool:
        """Updates a specific field in the profile."""
        profile = self.load_profile()
        profile[field] = value
        return self.save_profile(profile)

    def reset_profile(self) -> bool:
        """Resets the profile to the default template."""
        logger.info("Resetting user profile to defaults.")
        return self.save_profile(DEFAULT_PROFILE.copy())

# Shared global profile memory instance
profile_memory = ProfileMemory()
