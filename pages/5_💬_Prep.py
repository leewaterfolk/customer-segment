import streamlit as st
from lib.auth import require_auth
from lib.claude_client import stream_chat

st.set_page_config(page_title="Prep — JobPA", page_icon="💬", layout="wide")
require_auth()

SYSTEM = """\
You are a demanding senior hiring manager conducting a real job interview.
You have thoroughly read the candidate's CV and job description.

Rules:
- Ask EXACTLY ONE question at a time. Never stack multiple questions.
- Start moderate (behavioural), escalate to hard (technical/situational).
- After EACH answer:
  SCORE: X/10 — [2-line rationale using STAR benchmark]
  TIP: [one concrete coaching note to improve the answer]
  Then ask the next question immediately.
- Be specific to the candidate's background and target role — no generic questions.
- After ALL rounds are complete, deliver:

## INTERVIEW SUMMARY
- Overall: [avg]/10
- Strongest answer: [question topic] — [why it worked]
- Weakest answer: [question topic] — [what was missing]
- Top 3 priorities before the real interview
"""

with st.sidebar:
    st.page_link("app.py", label="← Home", icon="🏠")
    if st.session_state.get("user_email"):
        st.caption(f"👤 {st.session_state.user_email}")
    st.divider()
    cv = st.text_area("Your CV", height=280,
                      placeholder="Paste your CV here…",
                      key="cv_global")
    jd = st.text_area("Job Description (optional)", height=140,
                      placeholder="Paste a JD for role-specific questions…",
                      key="jd_prep")
    rounds = st.slider("Number of questions", 3, 10, 5)

st.title("💬 Interview Simulator")
st.caption("The hardest questions in your field — every answer scored /10 with coaching.")

# ── Session init ──────────────────────────────────────────────────────────────
if "prep_messages" not in st.session_state:
    st.session_state.prep_messages = []
    st.session_state.prep_active = False
    st.session_state.prep_round = 0
    st.session_state.prep_rounds = 5

if st.button("Start Interview", type="primary"):
    if not cv.strip():
        st.warning("Paste your CV in the sidebar first.")
        st.stop()
    ctx = f"## Candidate CV\n\n{cv}"
    if jd.strip():
        ctx += f"\n\n---\n\n## Target Role\n\n{jd}"
    ctx += f"\n\n---\n\nConduct a {rounds}-question interview. Ask the first question now."
    st.session_state.prep_messages = [{"role": "user", "content": ctx}]
    st.session_state.prep_active = True
    st.session_state.prep_round = 0
    st.session_state.prep_rounds = rounds
    st.rerun()

# ── Conversation ──────────────────────────────────────────────────────────────
if st.session_state.prep_active or st.session_state.prep_messages:
    for msg in st.session_state.prep_messages[1:]:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    last_role = st.session_state.prep_messages[-1]["role"] if st.session_state.prep_messages else None

    if last_role == "user":
        with st.chat_message("assistant"):
            placeholder = st.empty()
            _, full = stream_chat(SYSTEM, st.session_state.prep_messages, placeholder)
        st.session_state.prep_messages.append({"role": "assistant", "content": full})
        st.session_state.prep_round += 1

        if st.session_state.prep_round >= st.session_state.prep_rounds:
            st.session_state.prep_messages.append({
                "role": "user",
                "content": "The interview is now complete. Please deliver the final INTERVIEW SUMMARY.",
            })
            st.session_state.prep_active = False
        st.rerun()

    if st.session_state.prep_active and last_role == "assistant":
        answer = st.chat_input(f"Your answer (Q{st.session_state.prep_round + 1}/{st.session_state.prep_rounds})…")
        if answer:
            st.session_state.prep_messages.append({"role": "user", "content": answer})
            st.rerun()

    if not st.session_state.prep_active and len(st.session_state.prep_messages) > 1:
        if st.button("Start over", type="secondary"):
            st.session_state.prep_messages = []
            st.session_state.prep_round = 0
            st.rerun()
