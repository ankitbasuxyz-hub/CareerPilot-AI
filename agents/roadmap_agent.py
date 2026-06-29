from typing import List, Dict, Any
from utils.logger import logger

# Pre-defined database of offline study resources & projects for various tech skills
SKILL_LEARNING_RESOURCES: Dict[str, Dict[str, Any]] = {
    "React": {
        "description": "Learn the core concepts of React, including components, state, props, and modern hooks (useState, useEffect).",
        "duration": "3 weeks (15 hours/week)",
        "resources": [
            {"name": "Official React Documentation", "url": "https://react.dev"},
            {"name": "Full Stack Open - React Section", "url": "https://fullstackopen.com/en/part1"}
        ],
        "projects": ["Build an Interactive Task Management Kanban Board using React state."]
    },
    "JavaScript": {
        "description": "Master ES6+ syntax, asynchronous programming (Promises, async/await), DOM manipulation, and closure scopes.",
        "duration": "2 weeks (10 hours/week)",
        "resources": [
            {"name": "MDN Web Docs - JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"},
            {"name": "JavaScript.info - Detailed Tutorial", "url": "https://javascript.info"}
        ],
        "projects": ["Build a Local Storage Weather App that fetches and formats offline mock data."]
    },
    "TypeScript": {
        "description": "Understand strong typing, interfaces, generic classes, and integrating TypeScript with frameworks.",
        "duration": "2 weeks (8 hours/week)",
        "resources": [
            {"name": "TypeScript Deep Dive Book", "url": "https://basarat.gitbook.io/typescript"},
            {"name": "TypeScript Official Handbook", "url": "https://www.typescriptlang.org/docs/"}
        ],
        "projects": ["Refactor a standard JavaScript Todo app into a strictly typed TypeScript application."]
    },
    "Python": {
        "description": "Deep dive into Python fundamentals, Object-Oriented Programming (OOP), file parsing, and REST Framework backends.",
        "duration": "3 weeks (12 hours/week)",
        "resources": [
            {"name": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/"},
            {"name": "Hitchhiker's Guide to Python", "url": "https://docs.python-guide.org/"}
        ],
        "projects": ["Write a command-line CSV Parser and Analyzer that outputs statistical JSON data."]
    },
    "PostgreSQL": {
        "description": "Learn relational database design, indexing, writing complex SQL JOINs, query tuning, and triggers.",
        "duration": "2 weeks (10 hours/week)",
        "resources": [
            {"name": "PostgreSQL Official Docs", "url": "https://www.postgresql.org/docs/"},
            {"name": "SQLZoo Database Exercises", "url": "https://sqlzoo.net/"}
        ],
        "projects": ["Design a relational database schema for an online library management system."]
    },
    "Docker": {
        "description": "Master containerization, writing Dockerfiles, managing container volumes, and docker-compose configurations.",
        "duration": "1 week (8 hours/week)",
        "resources": [
            {"name": "Docker Getting Started Guide", "url": "https://docs.docker.com/get-started/"},
            {"name": "Play with Docker Interactive Platform", "url": "https://labs.play-with-docker.com/"}
        ],
        "projects": ["Containerize a multi-service web app (frontend and database backend) using docker-compose."]
    },
    "Figma": {
        "description": "Understand UI/UX design tools: frames, vectors, components, auto-layout, interactive prototypes, and handoffs.",
        "duration": "2 weeks (12 hours/week)",
        "resources": [
            {"name": "Figma Learn Tutorials", "url": "https://help.figma.com/hc/en-us/categories/360002051614-Learn-Figma"},
            {"name": "UX Collective - Design Principles", "url": "https://uxdesign.cc"}
        ],
        "projects": ["Design a high-fidelity 5-screen interactive prototype for a mobile food delivery application."]
    },
    "Machine Learning": {
        "description": "Grasp core ML algorithms: supervised learning (regression, classification) and unsupervised clustering.",
        "duration": "4 weeks (15 hours/week)",
        "resources": [
            {"name": "Scikit-Learn Official User Guide", "url": "https://scikit-learn.org/stable/user_guide.html"},
            {"name": "Kaggle Course - Intro to Machine Learning", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"}
        ],
        "projects": ["Develop and evaluate a pipeline to predict house prices using regression models."]
    },
    "Kubernetes": {
        "description": "Learn container orchestration: pods, services, deployments, configmaps, and ingress routing.",
        "duration": "3 weeks (10 hours/week)",
        "resources": [
            {"name": "Kubernetes Interactive Tutorials", "url": "https://kubernetes.io/docs/tutorials/"},
            {"name": "KubeAcademy by VMware", "url": "https://kube.academy/"}
        ],
        "projects": ["Deploy a scalable, highly available web service on a local Minikube cluster."]
    },
    "LLMs": {
        "description": "Study transformer architectures, text generation, fine-tuning methodologies, and API integrations.",
        "duration": "2 weeks (10 hours/week)",
        "resources": [
            {"name": "Hugging Face NLP Course", "url": "https://huggingface.co/learn/nlp-course"},
            {"name": "Google AI Machine Learning Education", "url": "https://ai.google/education/"}
        ],
        "projects": ["Build an offline semantic text categorizer using pre-trained sentence embedders."]
    },
    "Prompt Engineering": {
        "description": "Explore systematic prompting techniques: few-shot learning, chain-of-thought, and output structuring.",
        "duration": "1 week (5 hours/week)",
        "resources": [
            {"name": "Prompt Engineering Guide", "url": "https://www.promptingguide.ai/"},
            {"name": "OpenAI CookBook", "url": "https://cookbook.openai.com/"}
        ],
        "projects": ["Draft an structured agent instructions suite that generates JSON outputs reliably."]
    }
}

class RoadmapAgent:
    """Specialist Agent that crafts learning roadmaps containing actionable resources and milestones."""

    def build_roadmap(self, missing_skills: List[str], target_role: str = "") -> List[Dict[str, Any]]:
        """
        Creates a list of learning modules tailored for the missing skills.
        If a skill is unknown, dynamically generates a generic module.
        """
        logger.info(f"Building learning roadmap for missing skills: {missing_skills}")
        
        roadmap_modules = []
        
        if not missing_skills:
            # If no skills are missing, generate advanced modules for professional growth
            roadmap_modules.append({
                "title": f"Advanced Mastery in {target_role or 'Tech'}",
                "description": "You have met all basic requirements! Focus on system architecture, code optimization, and leadership.",
                "duration": "4 weeks (8 hours/week)",
                "resources": [
                    {"name": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer"},
                    {"name": "Google Tech Dev Guide", "url": "https://techdevguide.withgoogle.com/"}
                ],
                "projects": ["Author an architectural review doc for a distributed high-throughput service."],
                "completed": False
            })
            return roadmap_modules

        for skill in missing_skills:
            matched_skill = None
            # Case insensitive check
            for k in SKILL_LEARNING_RESOURCES:
                if k.lower() == skill.lower() or k.lower() in skill.lower() or skill.lower() in k.lower():
                    matched_skill = k
                    break
            
            if matched_skill:
                info = SKILL_LEARNING_RESOURCES[matched_skill]
                roadmap_modules.append({
                    "title": f"Master {matched_skill}",
                    "description": info["description"],
                    "duration": info["duration"],
                    "resources": info["resources"],
                    "projects": info["projects"],
                    "completed": False
                })
            else:
                # Dynamic fallback generation
                roadmap_modules.append({
                    "title": f"Study {skill}",
                    "description": f"Learn the core elements, tooling ecosystem, and practical applications of {skill} inside a career environment.",
                    "duration": "2 weeks (8 hours/week)",
                    "resources": [
                        {"name": f"Search Guide for {skill}", "url": f"https://www.google.com/search?q={skill}+tutorial+docs"},
                        {"name": "Wikipedia Tech Article", "url": f"https://en.wikipedia.org/wiki/{skill}"}
                    ],
                    "projects": [f"Develop a repository showcasing practical implementation of {skill} best practices."],
                    "completed": False
                })
                
        logger.info(f"Built roadmap containing {len(roadmap_modules)} learning modules.")
        return roadmap_modules
