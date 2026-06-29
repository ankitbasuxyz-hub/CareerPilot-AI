from typing import Dict, List, Any
from utils.logger import logger

ROLE_REQUIRED_SKILLS: Dict[str, List[str]] = {
    "Frontend Developer": [
        "React", "JavaScript", "CSS", "HTML", "TypeScript",
        "Next.js", "Git", "Tailwind CSS", "REST APIs", "Responsive Design"
    ],
    "Backend Developer": [
        "Python", "Django", "PostgreSQL", "Docker", "Redis",
        "REST APIs", "Node.js", "SQL", "Git", "System Design"
    ],
    "Data Scientist": [
        "Python", "SQL", "Machine Learning", "Pandas", "Scikit-Learn",
        "TensorFlow", "Statistics", "Data Visualization", "Jupyter", "Git"
    ],
    "UX/UI Designer": [
        "Figma", "Wireframing", "Prototyping", "User Research",
        "UI Design", "Design Systems", "Usability Testing", "Typography", "Color Theory"
    ],
    "Product Manager": [
        "Agile", "Product Strategy", "Roadmapping", "Jira", "User Stories",
        "Market Research", "SQL", "Stakeholder Management", "A/B Testing", "Analytics"
    ],
    "Cloud Engineer": [
        "AWS", "Kubernetes", "Terraform", "Docker", "CI/CD",
        "Linux", "Bash Scripting", "IAM", "Cloud Architecture", "Monitoring"
    ],
    "Mobile Developer": [
        "Kotlin", "Swift", "Flutter", "React Native", "Git",
        "Mobile UI Design", "API Integration", "App Store Deployment", "Firebase"
    ],
    "AI Agent Developer": [
        "Python", "LLMs", "Prompt Engineering", "LangChain", "LlamaIndex",
        "Vector Databases", "API Integration", "MCP (Model Context Protocol)", "Git", "RAG"
    ]
}

class SkillGapAgent:
    """Specialist Agent that compares user skills against standard target role skillsets."""
    
    def __init__(self):
        self.role_skills = ROLE_REQUIRED_SKILLS

    def get_supported_roles(self) -> List[str]:
        """Returns lists of target roles supported by the engine."""
        return list(self.role_skills.keys())

    def get_required_skills(self, role: str) -> List[str]:
        """Returns standard required skills for a role."""
        return self.role_skills.get(role, ["Communication", "Problem Solving", "Adaptability"])

    def analyze_gap(self, user_skills: List[str], target_role: str) -> Dict[str, Any]:
        """
        Calculates skill match percentage, matching skills, and missing skills.
        """
        logger.info(f"Analyzing skill gap for role: '{target_role}' with user skills: {user_skills}")
        
        required = self.get_required_skills(target_role)
        if not required:
            return {
                "match_percentage": 0,
                "matching_skills": [],
                "missing_skills": []
            }
            
        user_skills_lower = [s.lower().strip() for s in user_skills]
        
        matching = []
        missing = []
        
        for req_skill in required:
            # Check if required skill is in user skills (substring case-insensitive match)
            is_match = False
            for user_skill in user_skills_lower:
                if user_skill == req_skill.lower() or user_skill in req_skill.lower() or req_skill.lower() in user_skill:
                    is_match = True
                    break
            
            if is_match:
                matching.append(req_skill)
            else:
                missing.append(req_skill)
                
        match_percentage = int((len(matching) / len(required)) * 100)
        
        analysis = {
            "match_percentage": match_percentage,
            "matching_skills": matching,
            "missing_skills": missing
        }
        
        logger.debug(f"Skill Gap results for {target_role}: {analysis}")
        return analysis
