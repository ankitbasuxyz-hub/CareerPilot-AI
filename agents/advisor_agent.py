from typing import Dict, List, Any
from utils.logger import logger

SALARY_DATA: Dict[str, Dict[str, str]] = {
    "Frontend Developer": {"Entry Level": "$60k - $85k", "Mid Level": "$90k - $125k", "Senior Level": "$130k - $185k"},
    "Backend Developer": {"Entry Level": "$65k - $90k", "Mid Level": "$95k - $135k", "Senior Level": "$140k - $190k"},
    "Data Scientist": {"Entry Level": "$70k - $95k", "Mid Level": "$105k - $145k", "Senior Level": "$150k - $215k"},
    "UX/UI Designer": {"Entry Level": "$55k - $80k", "Mid Level": "$85k - $115k", "Senior Level": "$120k - $165k"},
    "Product Manager": {"Entry Level": "$75k - $100k", "Mid Level": "$110k - $150k", "Senior Level": "$155k - $205k"},
    "Cloud Engineer": {"Entry Level": "$70k - $95k", "Mid Level": "$100k - $140k", "Senior Level": "$145k - $200k"},
    "Mobile Developer": {"Entry Level": "$65k - $85k", "Mid Level": "$90k - $125k", "Senior Level": "$130k - $180k"},
    "AI Agent Developer": {"Entry Level": "$85k - $115k", "Mid Level": "$125k - $170k", "Senior Level": "$175k - $250k"}
}

TRANSITION_ADVICE: Dict[str, str] = {
    "Frontend to AI Agent Developer": (
        "1. Leverage Javascript/Typescript skills for node-based tool integrations (MCP).\n"
        "2. Study Python, as it is the primary language for AI agent orchestrators (LangChain, ADK).\n"
        "3. Understand vector embeddings and semantic search (RAG architectures).\n"
        "4. Work on UI dashboards for monitoring agent steps (like Gradio or Streamlit)."
    ),
    "Backend to Cloud Engineer": (
        "1. Master infrastructure deployment pipelines using Terraform (IaC).\n"
        "2. Gain deep expertise in container orchestration (Kubernetes/EKS).\n"
        "3. Focus on cloud security permissions, IAM roles, and VPC networking.\n"
        "4. Learn site monitoring practices using Prometheus and Grafana."
    ),
    "UX/UI to Frontend Developer": (
        "1. Translate design prototypes into HTML and clean Semantic CSS (Tailwind).\n"
        "2. Learn JavaScript DOM interactions and stateful component logic (React).\n"
        "3. Study responsive layouts, flexbox, grid, and browser rendering engines.\n"
        "4. Practice Git and deployment platforms like Vercel or Netlify."
    ),
    "Product Manager to UX/UI Designer": (
        "1. Transition from managing requirements to wireframing visual interfaces (Figma).\n"
        "2. Lead user research, focus groups, and draft usability test plans.\n"
        "3. Study layout typography, color hierarchy, and grid design systems.\n"
        "4. Build a design portfolio showing your high-fidelity iterations."
    )
}

class CareerAdvisorAgent:
    """Specialist Agent providing long-term career advice, salary statistics, and transition roadmaps."""

    def get_salary_info(self, role: str, level: str) -> str:
        """Returns the offline estimated salary band for a specific role and level."""
        logger.info(f"Retrieving salary band for '{role}' at '{level}'")
        role_data = SALARY_DATA.get(role)
        if not role_data:
            # Fallback estimation
            return "$60k - $100k (estimated)"
        return role_data.get(level, "$90k - $130k (estimated)")

    def get_transition_guide(self, source_role: str, target_role: str) -> str:
        """Generates step-by-step guidance on changing career tracks."""
        key = f"{source_role} to {target_role}"
        logger.info(f"Retrieving career transition advice for '{key}'")
        
        # Check direct match by splitting by " to "
        for k, advice in TRANSITION_ADVICE.items():
            parts = k.split(" to ")
            if len(parts) == 2:
                k_src, k_tgt = parts[0].strip().lower(), parts[1].strip().lower()
                s_clean = source_role.lower()
                t_clean = target_role.lower()
                if (k_src in s_clean or s_clean.startswith(k_src)) and \
                   (k_tgt in t_clean or t_clean.startswith(k_tgt)):
                    return advice
                
        # Dynamic fallback advice if combination not cataloged
        return (
            f"Transitioning from '{source_role}' to '{target_role}' requires matching overlapping skills:\n"
            f"1. Audit common technical skills: both roles value project management, Git, and systematic problem solving.\n"
            f"2. Bridge knowledge gaps: identify the specific technical tools for '{target_role}' and build 2 portfolio projects.\n"
            f"3. Reposition your resume: describe your past experience in terms of outcomes relevant to '{target_role}' objectives.\n"
            f"4. Network: connect with professionals on LinkedIn who have made the identical shift."
        )

    def chat_advise(self, query: str, target_role: str = "", experience_level: str = "") -> str:
        """
        Conversational advisor interface that parses user inquiries offline
        and generates context-specific advice.
        """
        logger.info(f"Processing advisor chat query: '{query[:30]}...'")
        
        q_lower = query.lower()
        
        # 1. Salary Queries
        if any(w in q_lower for w in ["salary", "earn", "pay", "compensation", "package"]):
            role = target_role or "AI Agent Developer"
            level = experience_level or "Mid Level"
            band = self.get_salary_info(role, level)
            return (
                f"Based on current industry benchmarks, the estimated salary band for a **{level}** **{role}** "
                f"is approximately **{band}** per year.\n\n"
                f"**Salary Negotiation Tip:** Always research location-specific premiums, prepare three concrete "
                f"examples of how you solved business problems in your last role, and wait for the employer to make "
                f"the first financial offer if possible."
            )
            
        # 2. Transition Queries
        if any(w in q_lower for w in ["transition", "change career", "switch", "shift"]):
            source = "Software Developer"
            target = target_role or "AI Agent Developer"
            guide = self.get_transition_guide(source, target)
            return (
                f"Here is a recommended transition roadmap to pivot from **{source}** to **{target}**:\n\n"
                f"{guide}\n\n"
                f"Focus on building a portfolio project demonstrating your core transition skills."
            )
            
        # 3. Negotiation Advice
        if any(w in q_lower for w in ["negotiate", "offer", "counter"]):
            return (
                "When negotiating an offer, remember these three golden rules:\n"
                "1. **Never accept on the spot**: Thank them enthusiastically, request the offer in writing, and ask for 48 hours to review.\n"
                "2. **Quantify your leverage**: Frame your request in terms of the value you bring to their immediate problems (e.g., speed to deploy, scaling expertise).\n"
                "3. **Negotiate total package**: If salary is capped, request adjustments to signing bonuses, remote flexibility, or learning budgets."
            )

        # 4. Networking / Job Search advice
        if any(w in q_lower for w in ["job", "apply", "network", "linkedin", "resume", "interview"]):
            return (
                "To optimize your job search, shift from generic applications to targeted networking:\n"
                "- **Curated Applications**: Identify 10 target companies. Customize your resume to match their job description exactly.\n"
                "- **Informational Interviews**: Find engineers or PMs in those teams on LinkedIn. Ask for a 15-minute chat about their engineering culture, not a job.\n"
                "- **Proof of Work**: Publish short write-ups or open-source demos of your side projects. This acts as an active signal of your competencies."
            )

        # Default helpful career mentoring response
        return (
            "I'm here as your career mentor. You can ask me about:\n"
            f"- **Salary Estimates**: e.g., 'What is the salary for a senior {target_role or 'Frontend Developer'}?'\n"
            "- **Career Transitions**: e.g., 'How can I transition to an AI Engineer?'\n"
            "- **Negotiation & Offers**: e.g., 'How should I negotiate a remote developer offer?'\n"
            "- **Job Search Strategies**: e.g., 'How can I stand out on LinkedIn?'\n\n"
            "Tell me more about your current situation so I can give you custom suggestions!"
        )
