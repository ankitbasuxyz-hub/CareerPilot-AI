import json
import sys
from typing import List, Dict, Any
from fastmcp import FastMCP

# Ensure the parent directory is in search path
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger
from utils.security import validate_input_size, detect_prompt_injection, sanitize_output
from utils.memory import profile_memory
from agents.resume_agent import ResumeAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.roadmap_agent import RoadmapAgent
from agents.interview_agent import InterviewAgent
from agents.advisor_agent import CareerAdvisorAgent

# Initialize FastMCP Server
mcp = FastMCP("CareerPilot")

# Instantiate engines
resume_engine = ResumeAgent()
skill_engine = SkillGapAgent()
roadmap_engine = RoadmapAgent()
interview_engine = InterviewAgent()
advisor_engine = CareerAdvisorAgent()

@mcp.tool()
def analyze_resume_tool(resume_text: str, target_role: str = "") -> str:
    """
    Evaluates a resume against key structural categories and provides scores,
    strengths, weaknesses, and improvement checklists offline.
    """
    logger.info("MCP: analyze_resume_tool invoked")
    
    # 1. Security Check: Input Size
    if not validate_input_size(resume_text, max_chars=30000):
        return json.dumps({"error": "Input payload size exceeds safety threshold (30,000 chars)"})
        
    # 2. Security Check: Injection
    is_malicious, pattern = detect_prompt_injection(resume_text)
    if is_malicious:
        logger.warning(f"MCP Blocked: Malicious prompt injection keyword detected: '{pattern}'")
        return json.dumps({"error": "Request rejected due to potential prompt injection detection."})

    try:
        results = resume_engine.analyze_resume(resume_text, target_role)
        # 3. Security: Sanitize output fields
        results["strengths"] = [sanitize_output(s) for s in results["strengths"]]
        results["weaknesses"] = [sanitize_output(w) for w in results["weaknesses"]]
        results["suggestions"] = [sanitize_output(s) for s in results["suggestions"]]
        
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"MCP Tool Error: analyze_resume_tool: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def map_skills_tool(user_skills: List[str], target_role: str) -> str:
    """
    Calculates gaps between a list of user skills and role requirements.
    """
    logger.info(f"MCP: map_skills_tool invoked for role: {target_role}")
    try:
        results = skill_engine.analyze_gap(user_skills, target_role)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"MCP Tool Error: map_skills_tool: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def generate_roadmap_tool(missing_skills: List[str], target_role: str = "") -> str:
    """
    Builds a custom step-by-step learning roadmap for missing skills, including resources.
    """
    logger.info(f"MCP: generate_roadmap_tool invoked for {len(missing_skills)} missing skills")
    try:
        results = roadmap_engine.build_roadmap(missing_skills, target_role)
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"MCP Tool Error: generate_roadmap_tool: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def evaluate_interview_answer_tool(question: str, answer: str) -> str:
    """
    Scores an answer to a mock interview question, checking for length, STAR structure, and keywords.
    """
    logger.info("MCP: evaluate_interview_answer_tool invoked")
    
    # Security checks
    if not validate_input_size(answer, max_chars=10000):
        return json.dumps({"error": "Answer text exceeds allowed length (10,000 chars)"})
        
    is_malicious, pattern = detect_prompt_injection(answer)
    if is_malicious:
        return json.dumps({"error": "Malicious payload detected."})

    try:
        results = interview_engine.evaluate_response(question, answer)
        results["feedback"] = sanitize_output(results["feedback"])
        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"MCP Tool Error: evaluate_interview_answer_tool: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_salary_insights_tool(role: str, experience_level: str = "Mid Level") -> str:
    """
    Retrieves estimated yearly compensation ranges for roles and experience levels.
    """
    logger.info(f"MCP: get_salary_insights_tool invoked for {role} ({experience_level})")
    try:
        range_val = advisor_engine.get_salary_info(role, experience_level)
        return json.dumps({
            "role": role,
            "level": experience_level,
            "estimated_range": range_val
        }, indent=2)
    except Exception as e:
        logger.error(f"MCP Tool Error: get_salary_insights_tool: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def save_profile_tool(profile_json: str) -> str:
    """
    Saves the user profile state payload to local memory file database.
    """
    logger.info("MCP: save_profile_tool invoked")
    try:
        data = json.loads(profile_json)
        success = profile_memory.save_profile(data)
        return json.dumps({"success": success})
    except Exception as e:
        logger.error(f"MCP Tool Error: save_profile_tool: {e}")
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def load_profile_tool() -> str:
    """
    Loads and returns the current user profile state from database storage.
    """
    logger.info("MCP: load_profile_tool invoked")
    try:
        profile = profile_memory.load_profile()
        return json.dumps(profile, indent=2)
    except Exception as e:
        logger.error(f"MCP Tool Error: load_profile_tool: {e}")
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    logger.info("Starting CareerPilot FastMCP Server...")
    # FastMCP uses standard stdio transport as default
    mcp.run()
