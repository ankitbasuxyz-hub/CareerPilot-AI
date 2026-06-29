import pytest
from agents.resume_agent import ResumeAgent
from agents.skill_gap_agent import SkillGapAgent
from agents.roadmap_agent import RoadmapAgent
from agents.interview_agent import InterviewAgent
from agents.advisor_agent import CareerAdvisorAgent
from agents.coordinator import CoordinatorAgent
from utils.memory import profile_memory

@pytest.fixture
def resume_text():
    return (
        "John Doe\nEmail: john.doe@email.com\nPhone: 123-456-7890\n"
        "EDUCATION\nBachelor of Science in Computer Science, State University\n"
        "EXPERIENCE\nSoftware Engineer, Tech Corp (2 years)\n"
        "Developed web backends using Python and Django. Integrated Docker container setups.\n"
        "PROJECTS\nPersonal Website built in React.\n"
        "SKILLS\nPython, Django, React, Docker, SQL, Git, PostgreSQL"
    )

def test_resume_agent_parsing(resume_text):
    agent = ResumeAgent()
    skills = agent.parse_skills_from_text(resume_text)
    
    assert "Python" in skills
    assert "Django" in skills
    assert "React" in skills
    assert "Docker" in skills
    assert "SQL" in skills

def test_resume_agent_scoring(resume_text):
    agent = ResumeAgent()
    analysis = agent.analyze_resume(resume_text, "Backend Developer")
    
    assert analysis["score"] > 50
    assert len(analysis["strengths"]) >= 3
    assert not any("content is empty" in w for w in analysis["weaknesses"])

def test_skill_gap_agent():
    agent = SkillGapAgent()
    user_skills = ["Python", "SQL", "Git"]
    target_role = "Backend Developer"
    
    results = agent.analyze_gap(user_skills, target_role)
    
    assert results["match_percentage"] < 100
    assert "Python" in results["matching_skills"]
    assert "Docker" in results["missing_skills"]

def test_roadmap_agent():
    agent = RoadmapAgent()
    missing_skills = ["Docker", "PostgreSQL"]
    
    roadmap = agent.build_roadmap(missing_skills, "Backend Developer")
    
    assert len(roadmap) == 2
    assert "Master Docker" in roadmap[0]["title"]
    assert "Master PostgreSQL" in roadmap[1]["title"]
    assert roadmap[0]["completed"] is False

def test_interview_agent():
    agent = InterviewAgent()
    questions = agent.get_questions_for_role("Frontend Developer")
    
    assert len(questions) >= 4
    
    # Test short answer scoring
    short_eval = agent.evaluate_response(questions[0], "It is good.")
    assert short_eval["score"] <= 30
    
    # Test detailed answer scoring
    detailed_ans = (
        "In my last project, we noticed slow load times on mobile. My task was to optimize the bundle size. "
        "I implemented React lazy loading and code splitting, and replaced heavy libraries with lighter alternatives. "
        "Consequently, page loads improved by 40% and conversion rates increased significantly."
    )
    detailed_eval = agent.evaluate_response(questions[0], detailed_ans)
    assert detailed_eval["score"] >= 75
    assert "STAR method" in detailed_eval["feedback"]

def test_career_advisor_agent():
    agent = CareerAdvisorAgent()
    
    salary = agent.get_salary_info("AI Agent Developer", "Mid Level")
    assert "$125k" in salary
    
    transition = agent.get_transition_guide("Frontend Developer", "AI Agent Developer")
    assert "MCP" in transition
    
    chat_reply = agent.chat_advise("What is the pay for a senior developer?", "Frontend Developer", "Senior Level")
    assert "salary" in chat_reply.lower() or "compensation" in chat_reply.lower()

def test_coordinator_agent_workflow(resume_text):
    profile_memory.reset_profile()
    coordinator = CoordinatorAgent()
    
    profile = coordinator.process_user_resume(resume_text, "Backend Developer", "Mid Level")
    
    assert profile["target_role"] == "Backend Developer"
    assert profile["resume_score"] > 50
    assert len(profile["skills"]) >= 5
    assert len(profile["roadmap"]) >= 1
    
    # Test roadmap milestone updates
    updated_roadmap = coordinator.update_roadmap_milestone(0, True)
    assert updated_roadmap[0]["completed"] is True
    
    # Test interview start
    first_q = coordinator.start_mock_interview("Backend Developer")
    assert len(first_q) > 10
    
    # Test interview submission
    feedback, next_q, session, finished = coordinator.submit_interview_answer("I designed REST APIs using Django REST framework.")
    assert "Feedback" in feedback
    assert session["current_question_index"] == 1
    assert finished is False
