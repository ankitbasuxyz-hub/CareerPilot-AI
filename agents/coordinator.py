from typing import Dict, List, Any, Tuple
from utils.logger import logger
from utils.memory import profile_memory
from agents.resume_agent import ResumeAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.roadmap_agent import RoadmapAgent
from agents.interview_agent import InterviewAgent
from agents.advisor_agent import CareerAdvisorAgent

# Try importing Google ADK elements to demonstrate architectural alignment.
# If ADK is not installed locally, fall back to simulated native Python representations.
try:
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.adk.sessions import InMemorySessionService
    HAS_ADK = True
except ImportError:
    HAS_ADK = False
    # Fallback placeholder classes to guarantee offline execution safety
    class Agent:
        def __init__(self, name: str, instruction: str = "", tools: List[Any] = None):
            self.name = name
            self.instruction = instruction
            self.tools = tools or []
            
    class InMemorySessionService:
        pass
        
    class InMemoryRunner:
        def __init__(self, agent: Any, session_service: Any = None):
            self.agent = agent
            self.session_service = session_service

class CoordinatorAgent(Agent):
    """
    The master coordinator agent. Orchestrates user queries, directs them
    to specialized sub-agents, and manages conversational memory updates.
    """
    
    def __init__(self):
        # Configure system instruction
        instruction = (
            "You are the CareerPilot Coordinator Agent. You oversee career mentoring sessions, "
            "directing resume evaluation, skill gaps, learning plans, and interview mock roleplays."
        )
        super().__init__(name="CoordinatorAgent", instruction=instruction)
        
        # Instantiate local specialist agents
        self.resume_agent = ResumeAgent()
        self.skill_gap_agent = SkillGapAgent()
        self.roadmap_agent = RoadmapAgent()
        self.interview_agent = InterviewAgent()
        self.advisor_agent = CareerAdvisorAgent()
        
        logger.info(f"CoordinatorAgent initialized. Google ADK base loaded: {HAS_ADK}")

    def process_user_resume(self, resume_text: str, target_role: str, experience_level: str) -> Dict[str, Any]:
        """
        Executes end-to-end profile evaluation:
        1. Analyzes formatting completeness & scores resume.
        2. Extracts skills.
        3. Computes skill gaps against target role.
        4. Configures a custom roadmap.
        5. Saves updated state to persistent memory.
        """
        logger.info(f"Coordinator executing profile workflow. Target Role: {target_role}, Level: {experience_level}")
        
        # 1. Analyze and score resume
        resume_results = self.resume_agent.analyze_resume(resume_text, target_role)
        extracted_skills = resume_results["extracted_skills"]
        
        # 2. Analyze skill gaps
        gap_results = self.skill_gap_agent.analyze_gap(extracted_skills, target_role)
        missing_skills = gap_results["missing_skills"]
        
        # 3. Build personalized roadmap
        roadmap_modules = self.roadmap_agent.build_roadmap(missing_skills, target_role)
        
        # 4. Load, update, and commit profile state to persistent JSON
        profile = profile_memory.load_profile()
        profile["target_role"] = target_role
        profile["experience_level"] = experience_level
        profile["skills"] = extracted_skills
        profile["resume_raw"] = resume_text
        profile["resume_score"] = resume_results["score"]
        profile["resume_analysis"] = {
            "strengths": resume_results["strengths"],
            "weaknesses": resume_results["weaknesses"],
            "suggestions": resume_results["suggestions"]
        }
        profile["skill_gap"] = gap_results
        profile["roadmap"] = roadmap_modules
        
        # Reset interview active status if role changed
        if profile["interview_session"]["active"]:
            profile["interview_session"] = {
                "active": False,
                "current_question_index": -1,
                "questions": [],
                "answers": [],
                "feedback": []
            }
            
        profile_memory.save_profile(profile)
        logger.info("Coordinator completed resume workflow. Memory updated successfully.")
        return profile

    def update_roadmap_milestone(self, index: int, completed: bool) -> List[Dict[str, Any]]:
        """Updates the completion state of a specific roadmap module in persistent memory."""
        profile = profile_memory.load_profile()
        if 0 <= index < len(profile["roadmap"]):
            profile["roadmap"][index]["completed"] = completed
            profile_memory.save_profile(profile)
            logger.info(f"Roadmap module index {index} completion status set to {completed}")
        return profile["roadmap"]

    def start_mock_interview(self, target_role: str) -> str:
        """Initializes a new mock interview session and returns the first question."""
        logger.info(f"Starting mock interview simulation for role: {target_role}")
        questions = self.interview_agent.get_questions_for_role(target_role)
        
        session = {
            "active": True,
            "current_question_index": 0,
            "questions": questions,
            "answers": [],
            "feedback": []
        }
        
        profile_memory.update_field("interview_session", session)
        return questions[0]

    def submit_interview_answer(self, answer: str) -> Tuple[str, str, Dict[str, Any], bool]:
        """
        Submits answer, evaluates it, and advances the interview.
        Returns:
            feedback_text (str): Score review for the submitted answer.
            next_prompt (str): Next question prompt (or completion notice).
            session_state (dict): State copy.
            is_finished (bool): Flag indicating if interview is complete.
        """
        profile = profile_memory.load_profile()
        session = profile["interview_session"]
        
        if not session["active"]:
            return "No active interview session found.", "Please start a mock interview first.", session, True
            
        idx = session["current_question_index"]
        questions = session["questions"]
        
        if idx < 0 or idx >= len(questions):
            return "Interview is already complete.", "Check your scorecard below.", session, True
            
        current_question = questions[idx]
        
        # Evaluate current answer
        evaluation = self.interview_agent.evaluate_response(current_question, answer)
        
        # Append answer and feedback to session list
        session["answers"].append(answer)
        session["feedback"].append(evaluation)
        
        # Advance index
        next_idx = idx + 1
        session["current_question_index"] = next_idx
        
        is_finished = next_idx >= len(questions)
        next_prompt = ""
        feedback_text = (
            f"**Question {idx + 1} Feedback:**\n"
            f"- **Score:** {evaluation['score']}/100 ({evaluation['star_rating']})\n"
            f"- **Critique:** {evaluation['feedback']}\n"
        )
        
        if is_finished:
            session["active"] = False
            next_prompt = "### Mock Interview Complete!\nThank you for practicing. You can view your final scorecard below."
        else:
            next_prompt = f"**Question {next_idx + 1}:**\n{questions[next_idx]}"
            
        profile["interview_session"] = session
        profile_memory.save_profile(profile)
        
        return feedback_text, next_prompt, session, is_finished

    def get_advisor_response(self, query: str) -> str:
        """Retrieves career guidance response from the advisor agent and logs the interaction."""
        profile = profile_memory.load_profile()
        role = profile.get("target_role", "AI Agent Developer")
        level = profile.get("experience_level", "Mid Level")
        
        # Get advice
        response = self.advisor_agent.chat_advise(query, role, level)
        
        # Log to chat history
        profile["chat_history"].append({"user": query, "model": response})
        profile_memory.save_profile(profile)
        
        return response
