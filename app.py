import gradio as gr
import os
import sys
from typing import List, Dict, Any, Tuple

# Ensure the parent directory is in search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import logger
from utils.security import sanitize_user_input, validate_input_size, detect_prompt_injection
from utils.memory import profile_memory
from agents.coordinator import CoordinatorAgent
from agents.skill_gap_agent import ROLE_REQUIRED_SKILLS

# Initialize orchestrator
coordinator = CoordinatorAgent()

# Custom CSS for Premium Design & Micro-animations
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Apply font to entire app */
body, .gradio-container {
    font-family: 'Outfit', sans-serif !important;
}

/* Glassmorphism Title Header */
.header-container {
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.15) 0%, rgba(147, 51, 234, 0.15) 100%);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
}

.title-text {
    background: linear-gradient(to right, #4F46E5, #9333EA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.05em;
}

.subtitle-text {
    font-size: 1.1rem;
    opacity: 0.85;
    margin-top: 6px;
}

/* Dashboard KPI Card Styling */
.kpi-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.kpi-card {
    flex: 1;
    min-width: 220px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(4px);
}

.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(79, 70, 229, 0.15);
    border-color: rgba(79, 70, 229, 0.4);
}

.kpi-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #4F46E5;
    margin: 6px 0;
}

.dark .kpi-value {
    color: #818CF8;
}

.kpi-label {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.7;
}

/* Custom Alert styling */
.alert-box {
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid transparent;
    margin-bottom: 12px;
}

.alert-warning {
    background-color: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.2);
    color: #EF4444;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(128, 128, 128, 0.3);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(128, 128, 128, 0.5);
}
"""

def generate_kpis_html(profile: Dict[str, Any]) -> str:
    """Generates styled HTML for the KPI dashboard cards."""
    score = profile.get("resume_score", 0)
    
    # Calculate Gaps
    gap_info = profile.get("skill_gap", {})
    missing_count = len(gap_info.get("missing_skills", []))
    match_pct = gap_info.get("match_percentage", 0)
    
    # Calculate completed roadmap items
    roadmap = profile.get("roadmap", [])
    completed_count = sum(1 for m in roadmap if m.get("completed", False))
    total_roadmap = len(roadmap)
    
    roadmap_str = f"{completed_count}/{total_roadmap}" if total_roadmap > 0 else "0/0"
    
    kpi_html = f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">Resume Readiness</div>
            <div class="kpi-value">{score}%</div>
            <div style="font-size: 0.8rem; opacity: 0.6;">Key section completeness</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Skill Gap Match</div>
            <div class="kpi-value">{match_pct}%</div>
            <div style="font-size: 0.8rem; opacity: 0.6;">{missing_count} missing skills</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Roadmap Milestones</div>
            <div class="kpi-value">{roadmap_str}</div>
            <div style="font-size: 0.8rem; opacity: 0.6;">Tasks checked off</div>
        </div>
    </div>
    """
    return kpi_html

def generate_profile_summary_html(profile: Dict[str, Any]) -> str:
    """Generates the HTML representation for the profile details on the dashboard."""
    role = profile.get("target_role", "None Selected")
    level = profile.get("experience_level", "None Selected")
    skills = profile.get("skills", [])
    
    skills_badges = "".join([f'<span style="background: rgba(79, 70, 229, 0.1); border: 1px solid rgba(79, 70, 229, 0.2); border-radius: 12px; padding: 4px 10px; margin: 4px; display: inline-block; font-size: 0.85rem;">{s}</span>' for s in skills])
    if not skills_badges:
        skills_badges = "<span style='opacity: 0.5;'>Paste/Analyze your resume to extract skills.</span>"
        
    summary_html = f"""
    <div style="padding: 16px; border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 10px; background: rgba(128, 128, 128, 0.02);">
        <h3 style="margin-top: 0; border-bottom: 1px solid rgba(128, 128, 128, 0.15); padding-bottom: 8px;">Target Profile</h3>
        <p style="margin: 6px 0;"><strong>Role:</strong> {role}</p>
        <p style="margin: 6px 0;"><strong>Level:</strong> {level}</p>
        <div style="margin-top: 12px;">
            <strong>Parsed Skills:</strong>
            <div style="margin-top: 6px;">{skills_badges}</div>
        </div>
    </div>
    """
    return summary_html

def generate_roadmap_html(profile: Dict[str, Any]) -> str:
    """Generates an aesthetic HTML presentation of the roadmap."""
    roadmap = profile.get("roadmap", [])
    if not roadmap:
        return "<p style='opacity: 0.6; text-align: center; padding: 40px;'>No active learning roadmap. Paste your resume in the 'Resume Review' tab to begin.</p>"
        
    html = '<div style="display: flex; flex-direction: column; gap: 16px; margin-top: 10px;">'
    for i, m in enumerate(roadmap):
        title = m.get("title", "")
        desc = m.get("description", "")
        dur = m.get("duration", "")
        projs = m.get("projects", [])
        res = m.get("resources", [])
        status = "✅ Done" if m.get("completed", False) else "⏳ Pending"
        
        resources_html = ", ".join([f'<a href="{r["url"]}" target="_blank" style="color: #4F46E5; text-decoration: underline;">{r["name"]}</a>' for r in res])
        projects_html = "".join([f'<li style="margin: 4px 0;">{p}</li>' for p in projs])
        
        html += f"""
        <div style="border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 10px; padding: 16px; background: rgba(128, 128, 128, 0.01); display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(128, 128, 128, 0.1); padding-bottom: 6px;">
                <h4 style="margin: 0; font-size: 1.1rem; font-weight: 600;">Module {i+1}: {title}</h4>
                <span style="font-size: 0.85rem; padding: 3px 8px; border-radius: 12px; background: rgba(128, 128, 128, 0.1); font-weight: 500;">{status}</span>
            </div>
            <p style="margin: 0; font-size: 0.95rem; opacity: 0.85;">{desc}</p>
            <p style="margin: 0; font-size: 0.9rem;"><strong>Estimated Duration:</strong> {dur}</p>
            <p style="margin: 0; font-size: 0.9rem;"><strong>Study Resources:</strong> {resources_html}</p>
            <div style="margin-top: 4px; font-size: 0.9rem;">
                <strong>Milestone Project:</strong>
                <ul style="margin: 4px 0; padding-left: 20px;">{projects_html}</ul>
            </div>
        </div>
        """
    html += '</div>'
    return html

def generate_interview_scorecard_html(session: Dict[str, Any]) -> str:
    """Generates HTML rendering of the mock interview history scorecard."""
    answers = session.get("answers", [])
    feedback_list = session.get("feedback", [])
    questions = session.get("questions", [])
    
    if not answers:
        return "<p style='opacity: 0.6; text-align: center; padding: 20px;'>Start the interview and submit answers to compile your scorecard.</p>"
        
    html = '<div style="display: flex; flex-direction: column; gap: 14px; margin-top: 10px;">'
    for i, ans in enumerate(answers):
        q = questions[i]
        fb = feedback_list[i]
        score = fb.get("score", 0)
        rating = fb.get("star_rating", "Basic")
        critique = fb.get("feedback", "")
        
        html += f"""
        <div style="border: 1px solid rgba(128, 128, 128, 0.15); border-radius: 8px; padding: 12px; background: rgba(128, 128, 128, 0.01);">
            <p style="margin: 0 0 6px 0; font-size: 0.9rem; font-weight: 500;"><strong>Question {i+1}:</strong> {q}</p>
            <p style="margin: 0 0 6px 0; font-size: 0.85rem; background: rgba(128, 128, 128, 0.05); padding: 6px; border-radius: 4px;"><strong>Your Answer:</strong> {ans}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed rgba(128, 128, 128, 0.15); padding-top: 6px; font-size: 0.85rem;">
                <span><strong>Grade Score:</strong> <span style="color: #4F46E5; font-weight: 600;">{score}/100</span> ({rating})</span>
            </div>
            <p style="margin: 6px 0 0 0; font-size: 0.85rem; opacity: 0.85;"><strong>Mentor Feedback:</strong> {critique}</p>
        </div>
        """
    html += '</div>'
    return html

# App Logic Handlers
def handle_resume_submission(resume_text: str, target_role: str, experience_level: str) -> Tuple[str, str, Dict[str, Any], Dict[str, Any], gr.CheckboxGroup, str]:
    """Processes user resume and reloads all UI views."""
    # Sanitize & Validate input
    resume_text = sanitize_user_input(resume_text)
    
    # Security checks
    if not validate_input_size(resume_text, max_chars=35000):
        return (
            "<div class='alert-box alert-warning'>Error: Resume size exceeds safe threshold (35,000 characters). Please condense.</div>",
            "", gr.update(), gr.update(), gr.update(), ""
        )
        
    is_malicious, pattern = detect_prompt_injection(resume_text)
    if is_malicious:
        logger.warning("Resume upload blocked due to prompt injection check.")
        return (
            "<div class='alert-box alert-warning'>Error: Resume content contains disallowed system override instructions.</div>",
            "", gr.update(), gr.update(), gr.update(), ""
        )

    # Process via coordinator
    profile = coordinator.process_user_resume(resume_text, target_role, experience_level)
    
    # Generate updated HTML structures
    kpis_html = generate_kpis_html(profile)
    summary_html = generate_profile_summary_html(profile)
    roadmap_html = generate_roadmap_html(profile)
    
    # Format Strengths, Weaknesses, Suggestions
    analysis = profile.get("resume_analysis", {})
    strengths = "\n".join([f"✅ {s}" for s in analysis.get("strengths", [])])
    weaknesses = "\n".join([f"❌ {w}" for w in analysis.get("weaknesses", [])])
    suggestions = "\n".join([f"💡 {s}" for s in analysis.get("suggestions", [])])
    
    # Format checkbox labels
    roadmap = profile.get("roadmap", [])
    cb_labels = [f"Module {i+1}: {m['title']} ({m['duration']})" for i, m in enumerate(roadmap)]
    cb_values = [cb_labels[i] for i, m in enumerate(roadmap) if m.get("completed", False)]
    
    result_msg = f"### Profile Analyzed Successfully!\nOverall Resume Score: **{profile.get('resume_score', 0)}/100**."
    
    return kpis_html, summary_html, strengths, weaknesses, suggestions, result_msg, roadmap_html, gr.update(choices=cb_labels, value=cb_values)

def handle_roadmap_checkbox_toggle(selected_titles: List[str]) -> Tuple[str, str]:
    """Updates completed roadmap tasks based on checkbox events."""
    profile = profile_memory.load_profile()
    roadmap = profile.get("roadmap", [])
    
    # Match selected titles by parsing the index from "Module X"
    for i, m in enumerate(roadmap):
        label = f"Module {i+1}: {m['title']} ({m['duration']})"
        m["completed"] = label in selected_titles
        
    # Save back
    profile_memory.save_profile(profile)
    
    # Re-render KPIs and Roadmap
    kpis_html = generate_kpis_html(profile)
    roadmap_html = generate_roadmap_html(profile)
    
    return kpis_html, roadmap_html

def handle_start_interview(target_role: str) -> Tuple[List[Dict[str, Any]], str, str, str]:
    """Resets interview states and prompts the first question."""
    first_q = coordinator.start_mock_interview(target_role)
    
    chat_history = [
        {"role": "assistant", "content": f"Welcome to your mock interview for **{target_role}**. Let's begin!\n\n**Question 1:** {first_q}"}
    ]
    
    scorecard_html = generate_interview_scorecard_html(profile_memory.load_profile()["interview_session"])
    return chat_history, scorecard_html, "", gr.update(interactive=True), gr.update(interactive=True)

def handle_interview_message(user_message: str, chat_history: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str, str, str, str]:
    """Evaluates answer, appends message logs, and displays next question."""
    user_message = sanitize_user_input(user_message)
    if not user_message:
        return chat_history, gr.update(), "", "", ""
        
    # Validate Size & Injection
    if not validate_input_size(user_message, max_chars=8000):
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": "⚠️ Error: Your response length exceeds size thresholds."})
        return chat_history, gr.update(), "", "", ""
        
    is_malicious, pattern = detect_prompt_injection(user_message)
    if is_malicious:
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": "⚠️ Response rejected due to safety policy block."})
        return chat_history, gr.update(), "", "", ""

    # Append user message
    chat_history.append({"role": "user", "content": user_message})
    
    # Process answer via coordinator
    feedback_text, next_prompt, session, is_finished = coordinator.submit_interview_answer(user_message)
    
    # Append feedback message
    chat_history.append({"role": "assistant", "content": f"{feedback_text}\n\n{next_prompt}"})
    
    # Render updated scorecard
    scorecard_html = generate_interview_scorecard_html(session)
    
    # Disable controls if complete
    input_update = gr.update(interactive=not is_finished, placeholder="Interview completed." if is_finished else "Type your answer here...")
    btn_update = gr.update(interactive=not is_finished)
    
    return chat_history, scorecard_html, "", input_update, btn_update

def handle_advisor_chat(message: str, history: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """Processes advisor questions and logs to conversation list."""
    message = sanitize_user_input(message)
    if not message:
        return "", history
        
    # Security check
    is_malicious, pattern = detect_prompt_injection(message)
    if is_malicious:
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": "⚠️ Malicious message filtered. Please rephrase."})
        return "", history

    history.append({"role": "user", "content": message})
    
    # Get answer
    reply = coordinator.get_advisor_response(message)
    history.append({"role": "assistant", "content": reply})
    
    return "", history

def handle_chip_click(chip_text: str, history: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """Automates message execution when pre-filled chip buttons are clicked."""
    return handle_advisor_chat(chip_text, history)

# Load Initial profile data
def load_app_defaults() -> Tuple[str, str, str, str, str, str, gr.update, List[Dict[str, Any]], List[Dict[str, Any]], str]:
    profile = profile_memory.load_profile()
    
    kpis = generate_kpis_html(profile)
    summary = generate_profile_summary_html(profile)
    roadmap_html = generate_roadmap_html(profile)
    
    analysis = profile.get("resume_analysis", {})
    strengths = "\n".join([f"✅ {s}" for s in analysis.get("strengths", [])])
    weaknesses = "\n".join([f"❌ {w}" for w in analysis.get("weaknesses", [])])
    suggestions = "\n".join([f"💡 {s}" for s in analysis.get("suggestions", [])])
    
    # Format checklists
    roadmap = profile.get("roadmap", [])
    cb_labels = [f"Module {i+1}: {m['title']} ({m['duration']})" for i, m in enumerate(roadmap)]
    cb_values = [cb_labels[i] for i, m in enumerate(roadmap) if m.get("completed", False)]
    
    # Interview chat default
    interview_session = profile.get("interview_session", {})
    interview_chat = []
    if interview_session.get("answers"):
        # Compile historical chat messages
        questions = interview_session.get("questions", [])
        answers = interview_session.get("answers", [])
        feedback = interview_session.get("feedback", [])
        for i, q in enumerate(questions):
            if i < len(answers):
                interview_chat.append({"role": "assistant", "content": f"**Question {i+1}:** {q}"})
                interview_chat.append({"role": "user", "content": answers[i]})
                fb = feedback[i]
                interview_chat.append({"role": "assistant", "content": f"**Question {i+1} Feedback:**\nScore: {fb['score']}/100 ({fb['star_rating']})\n{fb['feedback']}"})
        # Add next question if active
        if interview_session.get("active") and interview_session.get("current_question_index") < len(questions):
            curr_idx = interview_session["current_question_index"]
            interview_chat.append({"role": "assistant", "content": f"**Question {curr_idx+1}:** {questions[curr_idx]}"})
    else:
        interview_chat.append({"role": "assistant", "content": "Welcome to your mock interview coach! Click 'Start Mock Interview' above to begin."})
        
    scorecard = generate_interview_scorecard_html(interview_session)
    
    # Advisor chat default
    advisor_chat = []
    chat_hist = profile.get("chat_history", [])
    if chat_hist:
        for turn in chat_hist:
            advisor_chat.append({"role": "user", "content": turn["user"]})
            advisor_chat.append({"role": "assistant", "content": turn["model"]})
    else:
        target_role = profile.get("target_role", "AI Agent Developer")
        advisor_chat.append({"role": "assistant", "content": f"Hello! I am your career advisor. Ask me anything about career growth, salaries, or transition strategies for a **{target_role}**."})
        
    raw_resume = profile.get("resume_raw", "")
    
    return (
        kpis, summary, raw_resume, strengths, weaknesses, suggestions, 
        gr.update(choices=cb_labels, value=cb_values),
        interview_chat, scorecard, advisor_chat, roadmap_html
    )

# --- Gradio UI Layout Design ---
with gr.Blocks() as demo:
    
    # Header Banner
    with gr.Column(elem_classes="header-container"):
        gr.HTML(
            '<div style="display: flex; align-items: center; gap: 16px;">'
            '  <span style="font-size: 2.8rem;">🚀</span>'
            '  <div>'
            '    <h1 class="title-text">CareerPilot AI</h1>'
            '    <p class="subtitle-text">Your offline, multi-agent career copilot for resume analysis, skill mapping, and interview simulation.</p>'
            '  </div>'
            '</div>'
        )
    
    # Active KPI Dashboard Overview
    dashboard_kpis = gr.HTML()
    
    with gr.Tabs():
        
        # TAB 1: Profile & Progress Dashboard
        with gr.TabItem("📊 Dashboard"):
            with gr.Row():
                with gr.Column(scale=4):
                    gr.Markdown("### 👤 Professional Profile Summary")
                    profile_summary_view = gr.HTML()
                with gr.Column(scale=6):
                    gr.Markdown("### 📈 Learning Roadmap Progress")
                    roadmap_view_dash = gr.HTML()

        # TAB 2: Resume Scanning & Assessment
        with gr.TabItem("📄 Resume Review"):
            with gr.Row():
                with gr.Column(scale=5):
                    gr.Markdown("### 📝 Submit Profile details")
                    
                    target_role_input = gr.Dropdown(
                        choices=coordinator.skill_gap_agent.get_supported_roles(),
                        value="AI Agent Developer",
                        label="Target Career Role"
                    )
                    exp_level_input = gr.Dropdown(
                        choices=["Entry Level", "Mid Level", "Senior Level"],
                        value="Mid Level",
                        label="Experience Level Target"
                    )
                    resume_input = gr.Textbox(
                        lines=12,
                        placeholder="Paste your plain-text resume or copy-paste raw CV details here...",
                        label="Raw Resume Text"
                    )
                    
                    analyze_btn = gr.Button("🔍 Analyze Profile & Customize Plan", variant="primary")
                    analysis_result_md = gr.Markdown()
                    
                with gr.Column(scale=5):
                    gr.Markdown("### 📈 Assessment Feedback")
                    
                    with gr.Accordion("Strengths & Achievements", open=True):
                        strengths_output = gr.Textbox(label="Identified Strengths", lines=4, interactive=False)
                    with gr.Accordion("Key Gaps & Weaknesses", open=True):
                        weaknesses_output = gr.Textbox(label="Identified Gaps", lines=4, interactive=False)
                    with gr.Accordion("Actionable Improvements", open=True):
                        suggestions_output = gr.Textbox(label="Suggestions for Improvement", lines=5, interactive=False)

        # TAB 3: Skill Gap & Roadmap Planner
        with gr.TabItem("🛣️ Learning Roadmap"):
            gr.Markdown("### 🗺️ Your Personalized Learning Roadmap")
            gr.Markdown("Check off each module as you complete it. Your dashboard KPI readiness score will automatically update!")
            
            with gr.Row():
                with gr.Column(scale=4):
                    gr.Markdown("#### 📋 Task Checklist")
                    roadmap_checklist = gr.CheckboxGroup(
                        choices=[],
                        label="Milestones Checklist",
                        info="Check to mark completed"
                    )
                with gr.Column(scale=6):
                    gr.Markdown("#### 📖 Learning Content & Project Briefs")
                    roadmap_detail_view = gr.HTML()

        # TAB 4: Mock Interview Simulator
        with gr.TabItem("🎙️ Mock Interview"):
            gr.Markdown("### 🗣️ Interactive Mock Interview Training")
            gr.Markdown("Practice role-specific interview rounds. The coach evaluates your answers on detail, STAR framework, and keywords.")
            
            with gr.Row():
                with gr.Column(scale=6):
                    interview_chatbot = gr.Chatbot(label="Mock Interview Coach", height=450)
                    
                    with gr.Row():
                        interview_input = gr.Textbox(
                            show_label=False,
                            placeholder="Type your answer here...",
                            scale=8,
                            interactive=False
                        )
                        interview_send = gr.Button("Send", scale=2, variant="primary", interactive=False)
                        
                    with gr.Row():
                        start_interview_btn = gr.Button("🏁 Start New Interview", variant="secondary")
                        
                with gr.Column(scale=4):
                    gr.Markdown("#### 📊 Question Evaluation Scorecard")
                    interview_scorecard_view = gr.HTML()

        # TAB 5: Conversational Career Advisor
        with gr.TabItem("💡 Career Advisor"):
            gr.Markdown("### 💬 Mentor Advisory Chat")
            gr.Markdown("Ask questions about salaries, job negotiations, networking, or how to pivot between disciplines.")
            
            advisor_chatbot = gr.Chatbot(label="Career Mentor", height=400)
            advisor_input = gr.Textbox(
                show_label=False,
                placeholder="Ask your career advisor... (e.g. 'What is the salary for an AI Agent Developer?')"
            )
            
            # Recommendation Chips
            gr.Markdown("💡 **Quick Advice Chips:** Click a button below to ask immediately:")
            with gr.Row():
                chip1 = gr.Button("💰 Estimate AI Developer Salary", size="sm")
                chip2 = gr.Button("🤝 Negotiate remote developer offer", size="sm")
                chip3 = gr.Button("🛤️ Transition path: PM to Designer", size="sm")
    
    # Event wiring
    # Page Load default loading
    demo.load(
        load_app_defaults,
        outputs=[
            dashboard_kpis, profile_summary_view, resume_input, 
            strengths_output, weaknesses_output, suggestions_output, 
            roadmap_checklist, interview_chatbot, interview_scorecard_view, 
            advisor_chatbot, roadmap_detail_view
        ]
    )

    # Resume submit button click
    analyze_btn.click(
        handle_resume_submission,
        inputs=[resume_input, target_role_input, exp_level_input],
        outputs=[
            dashboard_kpis, profile_summary_view, strengths_output, 
            weaknesses_output, suggestions_output, analysis_result_md, 
            roadmap_detail_view, roadmap_checklist
        ]
    )

    # Roadmap checklist checkbox click
    roadmap_checklist.select(
        handle_roadmap_checkbox_toggle,
        inputs=[roadmap_checklist],
        outputs=[dashboard_kpis, roadmap_detail_view]
    )

    # Start mock interview click
    start_interview_btn.click(
        handle_start_interview,
        inputs=[target_role_input],
        outputs=[
            interview_chatbot, interview_scorecard_view, 
            interview_input, interview_input, interview_send
        ]
    )

    # Submit mock interview answer
    gr.on(
        triggers=[interview_input.submit, interview_send.click],
        fn=handle_interview_message,
        inputs=[interview_input, interview_chatbot],
        outputs=[
            interview_chatbot, interview_scorecard_view, 
            interview_input, interview_input, interview_send
        ]
    )

    # Submit career advisor question
    advisor_input.submit(
        handle_advisor_chat,
        inputs=[advisor_input, advisor_chatbot],
        outputs=[advisor_input, advisor_chatbot]
    )

    # Chip button events
    chip1.click(
        handle_chip_click,
        inputs=[gr.State("Estimate my target role salary in mid level"), advisor_chatbot],
        outputs=[advisor_input, advisor_chatbot]
    )
    chip2.click(
        handle_chip_click,
        inputs=[gr.State("Give me remote developer offer negotiation tips"), advisor_chatbot],
        outputs=[advisor_input, advisor_chatbot]
    )
    chip3.click(
        handle_chip_click,
        inputs=[gr.State("How do I transition from a Product Manager to UX/UI designer?"), advisor_chatbot],
        outputs=[advisor_input, advisor_chatbot]
    )

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 7860))
    logger.info(f"Starting Gradio web UI at http://{host}:{port}")
    demo.launch(
        server_name=host,
        server_port=port,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="slate")
    )
