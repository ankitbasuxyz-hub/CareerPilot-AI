import re
from typing import Dict, List, Any
from utils.logger import logger
from agents.skill_gap_agent import ROLE_REQUIRED_SKILLS

class ResumeAgent:
    """Specialist Agent that parses and scores resumes, extracting skills and providing feedback."""
    
    def __init__(self):
        # Flatten all known skills for keyword matching
        self.all_known_skills = set()
        for skills in ROLE_REQUIRED_SKILLS.values():
            for s in skills:
                self.all_known_skills.add(s)
                # Split multi-word skills to catch individual terms
                if " " in s:
                    self.all_known_skills.update(s.split())
        
        # Add common synonyms or generic terms
        self.all_known_skills.update([
            "java", "c++", "c#", "html5", "css3", "bootstrap", "angular", "vue",
            "flask", "fastapi", "mysql", "mongodb", "sqlite", "git", "github", 
            "gitlab", "heroku", "netlify", "scrum", "kanban", "communication", 
            "leadership", "teamwork", "problem solving", "analytical", "office"
        ])

    def parse_skills_from_text(self, text: str) -> List[str]:
        """Extracts skills from text by checking against known skills."""
        if not text:
            return []
            
        extracted = set()
        text_lower = text.lower()
        
        # Check standard multi-word skills first to prevent split match
        multi_word_skills = [s for s in ROLE_REQUIRED_SKILLS.values()]
        # Flatten and filter
        flat_skills = []
        for fl in multi_word_skills:
            flat_skills.extend(fl)
        
        for skill in set(flat_skills):
            if len(skill) > 3 and skill.lower() in text_lower:
                extracted.add(skill)
                
        # Word boundary search for single words
        words = re.findall(r"\b[a-zA-Z\+\#\-]{2,15}\b", text_lower)
        for w in words:
            for s in self.all_known_skills:
                if w == s.lower():
                    # Add capitalized version
                    extracted.add(s)
                    
        return sorted(list(extracted))

    def analyze_resume(self, resume_text: str, target_role: str = "") -> Dict[str, Any]:
        """
        Analyzes a resume against key sections and targets.
        Scores it from 0 to 100.
        """
        logger.info(f"Analyzing resume for role target: '{target_role}'")
        
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                "score": 0,
                "strengths": [],
                "weaknesses": ["Resume content is empty or too short."],
                "suggestions": ["Please paste or upload a complete resume to analyze."],
                "extracted_skills": []
            }
            
        text_lower = resume_text.lower()
        
        # Define checklist
        checks = {
            "contact_info": bool(re.search(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b", text_lower) or re.search(r"\b\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}\b", text_lower)),
            "experience": bool(re.search(r"\b(experience|work|employment|history|professional|career)\b", text_lower)),
            "education": bool(re.search(r"\b(education|degree|university|college|school|academic)\b", text_lower)),
            "projects": bool(re.search(r"\b(projects|portfolio|personal projects|key projects)\b", text_lower)),
            "skills_section": bool(re.search(r"\b(skills|technologies|expertise|proficiencies|tools)\b", text_lower))
        }
        
        strengths = []
        weaknesses = []
        suggestions = []
        
        score = 30 # Base score for submitting text
        
        # Score section existence
        if checks["contact_info"]:
            score += 10
            strengths.append("Contact details found (email/phone).")
        else:
            weaknesses.append("Missing clear email or phone contact details.")
            suggestions.append("Add your professional email address and phone number in a prominent header.")
            
        if checks["experience"]:
            score += 15
            strengths.append("Professional experience section detected.")
        else:
            weaknesses.append("No professional experience section identified.")
            suggestions.append("Create an 'Experience' section outlining your work history in reverse chronological order.")
            
        if checks["education"]:
            score += 10
            strengths.append("Education section detected.")
        else:
            weaknesses.append("No education details found.")
            suggestions.append("Add your educational background including degrees, majors, and universities.")
            
        if checks["projects"]:
            score += 10
            strengths.append("Projects section detected.")
        else:
            weaknesses.append("No projects section found.")
            suggestions.append("Incorporate a 'Projects' section showing practical application of your skills.")
            
        if checks["skills_section"]:
            score += 10
            strengths.append("Dedicated skills section identified.")
        else:
            weaknesses.append("Missing a distinct skills list section.")
            suggestions.append("Add a structured 'Technical Skills' section grouping technologies by category.")

        # Extract skills
        extracted_skills = self.parse_skills_from_text(resume_text)
        
        # Check role compatibility
        if target_role and target_role in ROLE_REQUIRED_SKILLS:
            required = ROLE_REQUIRED_SKILLS[target_role]
            role_matches = [s for s in required if s in extracted_skills]
            match_ratio = len(role_matches) / len(required) if required else 0
            
            role_score_addon = int(match_ratio * 15)
            score += role_score_addon
            
            if match_ratio >= 0.6:
                strengths.append(f"Strong keyword alignment with the '{target_role}' role requirements.")
            elif match_ratio >= 0.3:
                weaknesses.append(f"Moderate keyword gaps for the target role '{target_role}'.")
                suggestions.append(f"Integrate more key skills relevant to '{target_role}' (e.g., {', '.join(required[:3])}) into your experience descriptions.")
            else:
                weaknesses.append(f"Significant keyword gaps for the target role '{target_role}'.")
                suggestions.append(f"Tailor your resume specifically for '{target_role}' by highlighting projects involving: {', '.join(required[:5])}.")
        else:
            # Generic bonus for skill count
            if len(extracted_skills) >= 10:
                score += 15
                strengths.append("Rich portfolio of technical/soft skills parsed.")
            elif len(extracted_skills) >= 5:
                score += 10
                strengths.append("Good core skillset detected.")
            else:
                weaknesses.append("Very few technical skills identified.")
                suggestions.append("Expand your skills list to reflect all coding languages, tools, and methodologies you know.")

        # Final cap check
        score = min(max(score, 10), 100)
        
        analysis = {
            "score": score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "extracted_skills": extracted_skills
        }
        
        logger.info(f"Resume analysis complete. Score: {score}")
        return analysis
