#!/usr/bin/env python3
"""
app.py - JobPA Web UI
Run: streamlit run app.py
"""

import os
import sys
import streamlit as st
import anthropic

CV_DEFAULT_PATH = "cv_master.txt"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobPA — Beat the ATS",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
  .stTextArea textarea { font-family: monospace; font-size: 13px; }
  .score-badge {
    display: inline-block;
    background: #1a1a2e;
    color: #e94560;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 14px;
  }
  section.main > div { max-width: 900px; margin: auto; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 JobPA — Beat the ATS")
st.caption("The Résumé Loop: Diagnose → Refine → Rewrite → Prep")

# ── Sidebar: CV input ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Your Résumé")

    default_cv = ""
    if os.path.exists(CV_DEFAULT_PATH):
        with open(CV_DEFAULT_PATH, "r", encoding="utf-8") as f:
            default_cv = f.read()

    cv_text = st.text_area(
        "Paste your CV here",
        value=default_cv,
        height=400,
        placeholder="Paste your full CV / résumé text here...",
    )

    api_key = st.text_input(
        "Anthropic API Key",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Or set ANTHROPIC_API_KEY env var",
    )
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    st.divider()
    st.caption("Steps 01–04 of the résumé loop")

# ── Helper ───────────────────────────────────────────────────────────────────
def get_client():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        st.error("Set your Anthropic API key in the sidebar.")
        st.stop()
    return anthropic.Anthropic(api_key=key)

def check_cv():
    if not cv_text.strip():
        st.warning("Paste your CV in the sidebar first.")
        st.stop()

def stream_response(system_prompt: str, user_message: str, placeholder):
    client = get_client()
    full = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            full += text
            placeholder.markdown(full + "▌")
    placeholder.markdown(full)
    return stream.get_final_message(), full

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "01 · Diagnose",
    "02 · Refine",
    "03 · Rewrite",
    "04 · Prep",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 01 — DIAGNOSE
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("ATS Diagnostic")
    st.caption("See your résumé the way an ATS parses it — catch what breaks before you change a word.")

    if st.button("Run Diagnostic", type="primary", key="btn_diagnose"):
        check_cv()
        output = st.empty()
        DIAGNOSE_PROMPT = """\
You are an ATS (Applicant Tracking System) expert. Analyse this résumé exactly as a
modern ATS would, then give actionable feedback in these sections:

## ATS PARSE SCORE  /100
Overall compatibility score with 2-3 line justification.

## AUTO-REJECT TRIGGERS
List elements that cause instant rejection (formatting issues, missing contact info,
non-standard headings, date inconsistencies, graphics).
Format: "⚠ [Issue] — [Why it matters]"
If none: "✓ No auto-reject triggers detected."

## KEYWORD DENSITY
Top 10 keywords present (with frequency). Then 3-5 generic filler phrases to remove.

## STRUCTURE & SECTIONS
Score each: Contact Info / Summary / Work Experience / Education / Skills /
Certifications — (Present / Missing / Weak) with a brief note.

## TOP 5 QUICK WINS
Ordered by impact. Format: "1. [Action] → [Expected gain]"
"""
        with st.spinner("Analysing…"):
            final, _ = stream_response(
                DIAGNOSE_PROMPT,
                f"Please run a full ATS diagnostic on this résumé:\n\n{cv_text}",
                output,
            )
        st.caption(f"Tokens — input: {final.usage.input_tokens} / output: {final.usage.output_tokens}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 02 — REFINE
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Keyword Gap Analysis")
    st.caption("Run your CV against a real job description — surface exact keywords you're missing.")

    jd2 = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the job description here…",
        key="jd2",
    )

    if st.button("Analyse Gap", type="primary", key="btn_refine"):
        check_cv()
        if not jd2.strip():
            st.warning("Paste a job description above.")
            st.stop()
        output = st.empty()
        REFINE_PROMPT = """\
You are an expert career coach. Given a CV and a job description, produce:

1. **Tailored Bullet Points to Emphasise**
   5-8 existing achievements that best match this role, rewritten as punchy ATS-optimised
   bullets. Format: "• [Original context] → [Tailored version]"

2. **Missing Keywords & Gaps**
   Keywords/tools/certs in the JD absent from the CV. For each, suggest how to surface it.
   Format: "• [Keyword] — [Suggestion]"

Keep tone direct and professional. No fluff.
"""
        user_msg = f"## My CV\n\n{cv_text}\n\n---\n\n## Job Description\n\n{jd2}"
        with st.spinner("Analysing gap…"):
            final, _ = stream_response(REFINE_PROMPT, user_msg, output)
        st.caption(f"Tokens — input: {final.usage.input_tokens} / output: {final.usage.output_tokens}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 03 — REWRITE
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("XYZ Bullet Rewriter")
    st.caption("Accomplished **X**, as measured by **Y**, by doing **Z**.")

    jd3 = st.text_area(
        "Job Description (optional — helps target the rewrites)",
        height=150,
        placeholder="Paste a job description to focus the rewrites, or leave blank for generic…",
        key="jd3",
    )

    if st.button("Rewrite Bullets", type="primary", key="btn_rewrite"):
        check_cv()
        output = st.empty()
        REWRITE_PROMPT = """\
You are an expert résumé writer specialised in the XYZ formula:
"Accomplished [X], as measured by [Y], by doing [Z]."

Rewrite every experience bullet using XYZ. Rules:
1. Keep content truthful — never invent metrics. Write [METRIC NEEDED: e.g. "% improvement"]
   where data is missing.
2. Use strong action verbs. No "responsible for" or "helped with".
3. If a JD is provided, prioritise rewrites that surface the most relevant skills.
4. Output format for each bullet:
   ORIGINAL: <text>
   REWRITTEN: <XYZ version>
   (blank line between entries)
5. End with ## METRIC GAPS listing all placeholders so the candidate knows what to find.
"""
        user_msg = f"## CV\n\n{cv_text}"
        if jd3.strip():
            user_msg += f"\n\n---\n\n## Target Job Description\n\n{jd3}"
        user_msg += "\n\nPlease rewrite every experience bullet using the XYZ formula."
        with st.spinner("Rewriting…"):
            final, _ = stream_response(REWRITE_PROMPT, user_msg, output)
        st.caption(f"Tokens — input: {final.usage.input_tokens} / output: {final.usage.output_tokens}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 04 — PREP
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Interview Simulator")
    st.caption("The hardest questions in your field — every answer scored /10.")

    col1, col2 = st.columns([3, 1])
    with col1:
        jd4 = st.text_area(
            "Job Description (optional)",
            height=120,
            placeholder="Paste a JD to get role-specific questions…",
            key="jd4",
        )
    with col2:
        rounds = st.number_input("Questions", min_value=1, max_value=10, value=5, key="rounds")

    PREP_SYSTEM = """\
You are a demanding senior hiring manager conducting a real job interview.
You have read the candidate's CV and job description thoroughly.

Rules:
- Ask ONE question at a time. Never stack multiple questions.
- Start moderate, escalate to hard technical/situational questions.
- After each answer score it out of 10:
  SCORE: X/10 — [2-line rationale]
  TIP: [one specific coaching note]
  Then ask the next question.
- Use STAR as the benchmark for behavioural answers.
- Be specific to the candidate's background and target role.
- After all questions, produce:
  ## INTERVIEW SUMMARY
  - Overall score: [avg]/10
  - Strongest answer: [topic] — [why]
  - Weakest answer: [topic] — [why]
  - Top 3 coaching priorities
"""

    if "interview_messages" not in st.session_state:
        st.session_state.interview_messages = []
        st.session_state.interview_active = False
        st.session_state.interview_round = 0
        st.session_state.interview_rounds = 5

    if st.button("Start Interview", type="primary", key="btn_start_interview"):
        check_cv()
        st.session_state.interview_messages = []
        st.session_state.interview_active = True
        st.session_state.interview_round = 0
        st.session_state.interview_rounds = rounds

        context = f"## Candidate CV\n\n{cv_text}"
        if jd4.strip():
            context += f"\n\n---\n\n## Target Role\n\n{jd4}"
        context += f"\n\n---\n\nConduct a {rounds}-question interview. Ask the first question now."
        st.session_state.interview_messages.append({"role": "user", "content": context})

    if st.session_state.interview_active:
        # Show conversation history
        for msg in st.session_state.interview_messages[1:]:
            role = "🧑 You" if msg["role"] == "user" else "🎯 Interviewer"
            with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                st.markdown(msg["content"])

        # Get next AI response if last message was from user
        last_role = st.session_state.interview_messages[-1]["role"] if st.session_state.interview_messages else None
        if last_role == "user":
            with st.chat_message("assistant"):
                placeholder = st.empty()
                client = get_client()
                full = ""
                with client.messages.stream(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    system=PREP_SYSTEM,
                    messages=st.session_state.interview_messages,
                ) as stream:
                    for text in stream.text_stream:
                        full += text
                        placeholder.markdown(full + "▌")
                placeholder.markdown(full)
                st.session_state.interview_messages.append({"role": "assistant", "content": full})
                st.session_state.interview_round += 1

                if st.session_state.interview_round >= st.session_state.interview_rounds:
                    # Request summary
                    st.session_state.interview_messages.append({
                        "role": "user",
                        "content": "The interview is complete. Please provide the final INTERVIEW SUMMARY.",
                    })
                    st.session_state.interview_active = False
                    st.rerun()

        # Answer input
        if st.session_state.interview_active and st.session_state.interview_messages[-1]["role"] == "assistant":
            answer = st.chat_input("Your answer…")
            if answer:
                st.session_state.interview_messages.append({"role": "user", "content": answer})
                st.rerun()
