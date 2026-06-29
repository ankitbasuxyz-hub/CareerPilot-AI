from typing import List, Dict, Any, Tuple
from utils.logger import logger

# Role-specific mock interview questions database
ROLE_QUESTIONS: Dict[str, List[str]] = {
    "Frontend Developer": [
        "What is the difference between Virtual DOM and Shadow DOM, and how does React utilize the Virtual DOM?",
        "Can you explain JavaScript closures and describe a practical scenario where you would use them?",
        "How do you optimize a web application's page load performance (e.g., Next.js or React)?",
        "Describe a challenging front-end bug you solved. What was your debugging methodology?"
    ],
    "Backend Developer": [
        "Explain the differences between SQL and NoSQL databases. How do you decide which one to use?",
        "What is connection pooling, and why is it important for database connection management?",
        "How do you design a secure, high-throughput REST API that handles authentication and rate limiting?",
        "Tell me about a time you had to optimize a slow database query. What steps did you take?"
    ],
    "Data Scientist": [
        "What is overfitting in machine learning, and how do you prevent it?",
        "Can you explain the difference between L1 (Lasso) and L2 (Ridge) regularization?",
        "How would you handle highly imbalanced classes in a classification dataset?",
        "Describe a machine learning project you deployed. How did you monitor its prediction accuracy?"
    ],
    "UX/UI Designer": [
        "What is your user research methodology? How do you translate research findings into designs?",
        "Can you explain the concept of 'Design System' and how it improves design-to-development workflows?",
        "How do you handle stakeholder feedback that conflicts with usability test results?",
        "Walk me through a design decision you made that significantly improved a user metric."
    ],
    "Product Manager": [
        "How do you prioritize features on a product roadmap when stakeholders have conflicting demands?",
        "Tell me about a product you use daily. What is one feature you would add or improve, and why?",
        "How do you define and track success metrics (KPIs) for a newly launched feature?",
        "Describe a time a product launch failed or faced major delays. What did you learn?"
    ],
    "Cloud Engineer": [
        "What is Infrastructure as Code (IaC), and how does Terraform manage resources and state?",
        "Can you explain the difference between horizontal and vertical scaling in cloud environments?",
        "How would you design a disaster recovery plan for a multi-region microservices app?",
        "Describe an incident where a cloud service went down. How did you troubleshoot and resolve it?"
    ]
}

BEHAVIORAL_QUESTIONS: List[str] = [
    "Tell me about a time you worked on a project with tight deadlines. How did you organize your work?",
    "Describe a conflict you had with a team member. How did you resolve it, and what was the outcome?",
    "Give an example of a time you failed or made a mistake at work. How did you handle it?"
]

class InterviewAgent:
    """Specialist Agent that handles stateful mock interviews and evaluates user responses."""

    def get_questions_for_role(self, role: str) -> List[str]:
        """Fetches role-specific questions and appends behavioral questions."""
        questions = ROLE_QUESTIONS.get(role, [
            "Tell me about your background and how your skills fit a typical role in this industry.",
            "What is your process for learning a new technology or tool quickly?"
        ])
        # Add 1 behavioral question to shorten/focus the interview flow
        import random
        # Seed or select deterministic behavioral questions for reproducibility
        questions = list(questions) + [BEHAVIORAL_QUESTIONS[0], BEHAVIORAL_QUESTIONS[1]]
        return questions

    def evaluate_response(self, question: str, answer: str) -> Dict[str, Any]:
        """
        Scores a user's mock interview answer offline based on length,
        structure (STAR method check), and key technical terms.
        """
        logger.info(f"Evaluating answer for question: '{question[:30]}...'")
        
        if not answer or len(answer.strip()) < 15:
            return {
                "score": 20,
                "feedback": "Your response is too brief. In a real interview, aim to expand your answers. Explain the context, the action you took, and the final results using the STAR method (Situation, Task, Action, Result).",
                "star_rating": "Poor",
                "grammar_check": "Unable to verify due to short length."
            }

        word_count = len(answer.split())
        score = 50 # Base score for writing a reasonable answer
        feedback_points = []
        
        # 1. Word Count Scoring
        if word_count > 80:
            score += 15
            feedback_points.append("Excellent detail. Your response provides a thorough explanation.")
        elif word_count > 40:
            score += 10
            feedback_points.append("Good response length. You covered the core aspects.")
        else:
            score += 5
            feedback_points.append("Moderate length, but consider adding more context or specific technical examples.")

        # 2. Structure Scoring (STAR indicators)
        answer_lower = answer.lower()
        star_indicators = {
            "Situation/Task": ["situation", "task", "goal", "background", "project", "problem", "when I was", "role"],
            "Action": ["i did", "i resolved", "i created", "i built", "i designed", "i researched", "i implemented", "i analyzed"],
            "Result": ["result", "outcome", "consequently", "resolved", "improved", "saved", "increased", "learned", "delivered"]
        }
        
        structure_matches = 0
        for component, terms in star_indicators.items():
            if any(term in answer_lower for term in terms):
                structure_matches += 1
                
        if structure_matches == 3:
            score += 15
            feedback_points.append("Great structure! Your answer shows elements of Situation, Action, and Result (STAR method).")
        elif structure_matches == 2:
            score += 10
            feedback_points.append("Solid structure. Make sure you clearly highlight the positive 'Result' or outcome of your actions.")
        else:
            score += 5
            feedback_points.append("Your answer could benefit from a clearer structure. Start with the problem context, describe your exact actions, and state the final result.")

        # 3. Technical terminology check
        # Look for typical high-value professional words
        keywords = ["collaborated", "managed", "designed", "optimized", "scale", "performance", "testing", "metrics", "user", "solved"]
        keyword_matches = [w for w in keywords if w in answer_lower]
        if len(keyword_matches) >= 3:
            score += 10
            feedback_points.append(f"Used strong action verbs and professional terms (e.g., {', '.join(keyword_matches[:3])}).")
        elif len(keyword_matches) >= 1:
            score += 5
            
        score = min(max(score, 10), 100)
        
        # Star Rating label
        if score >= 85:
            rating = "Strong Match (Excellent)"
        elif score >= 70:
            rating = "Capable (Good)"
        elif score >= 50:
            rating = "Development Needed (Average)"
        else:
            rating = "Needs Practice (Basic)"

        return {
            "score": score,
            "feedback": " ".join(feedback_points),
            "star_rating": rating,
            "word_count": word_count
        }
