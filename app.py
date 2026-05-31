#!/usr/bin/env python3
"""
app.py - JobPA Web UI
Run: streamlit run app.py

Required env vars (set in Railway):
  ANTHROPIC_API_KEY   — Claude API key  (required)

Optional:
  WAITLIST_ENDPOINT   — a Formspree (or any) POST URL to collect emails.
                        If unset, emails are appended to local waitlist.txt.
                        Get a free one at https://formspree.io (form action URL).
"""

import os
import streamlit as st
import anthropic

# ── Config ───────────────────────────────────────────────────────────────────
CV_DEFAULT_PATH = "cv_master.txt"
WAITLIST_ENDPOINT = os.environ.get("WAITLIST_ENDPOINT", "")

st.set_page_config(
    page_title="JobPA — Beat the ATS",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
  * { box-sizing: border-box; }
  .stTextArea textarea { font-family: monospace; font-size: 13px; }

  /* Landing page */
  .hero { text-align: center; padding: 60px 20px 40px; }
  .hero h1 { font-size: 3rem; font-weight: 900; letter-spacing: -1px; margin-bottom: 8px; }
  .hero p { font-size: 1.2rem; color: #888; margin-bottom: 36px; }
  .steps-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
    max-width: 860px; margin: 0 auto 48px;
  }
  .step-card {
    background: #111; border: 1px solid #222; border-radius: 12px;
    padding: 24px 20px; text-align: center;
  }
  .step-num { font-size: 2rem; font-weight: 900; color: #e94560; }
  .step-title { font-size: 1rem; font-weight: 700; margin: 6px 0 4px; }
  .step-desc { font-size: 0.82rem; color: #777; line-height: 1.4; }
  .cta-row { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-bottom: 16px; }
  .btn-google {
    display: inline-flex; align-items: center; gap: 10px;
    background: #fff; color: #222; font-weight: 600;
    padding: 12px 28px; border-radius: 8px; text-decoration: none;
    font-size: 1rem; border: none; cursor: pointer;
  }
  .user-badge {
    background: #111; border: 1px solid #222; border-radius: 8px;
    padding: 8px 20px; display: inline-block; font-size: 0.9rem; color: #ccc;
  }
  section.main > div { max-width: 980px; margin: auto; }
</style>
""", unsafe_allow_html=True)

# ── Waitlist persistence ──────────────────────────────────────────────────────
def save_waitlist_email(email: str) -> tuple[bool, str]:
    """Returns (success, message). Posts to WAITLIST_ENDPOINT if set, else local file."""
    if WAITLIST_ENDPOINT:
        try:
            import urllib.request
            import json
            data = json.dumps({"email": email}).encode()
            req = urllib.request.Request(
                WAITLIST_ENDPOINT, data=data,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)
            return True, "You're on the list! We'll be in touch."
        except Exception as e:
            return False, f"Something went wrong: {e}"
    else:
        try:
            with open("waitlist.txt", "a", encoding="utf-8") as f:
                f.write(email + "\n")
            return True, "You're on the list!"
        except Exception as e:
            return False, f"Something went wrong: {e}"

# ── Session init ──────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None

# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE  (shown when not authenticated)
# ══════════════════════════════════════════════════════════════════════════════
def show_landing():
    st.markdown("""
<div class="hero">
  <h1>Beat the ATS.</h1>
  <p>The Résumé Loop — four steps from invisible to interview-ready.</p>
  <div class="steps-grid">
    <div class="step-card">
      <div class="step-num">01</div>
      <div class="step-title">Diagnose</div>
      <div class="step-desc">See your résumé the way an ATS parses it. Catch auto-rejects before you apply.</div>
    </div>
    <div class="step-card">
      <div class="step-num">02</div>
      <div class="step-title">Refine</div>
      <div class="step-desc">Run against real JDs. Surface the exact keywords you're missing.</div>
    </div>
    <div class="step-card">
      <div class="step-num">03</div>
      <div class="step-title">Rewrite</div>
      <div class="step-desc">Rebuild every bullet on the XYZ formula — quantified, punchy, ATS-ready.</div>
    </div>
    <div class="step-card">
      <div class="step-num">04</div>
      <div class="step-title">Prep</div>
      <div class="step-desc">AI hiring manager. Hardest questions in your field. Every answer scored /10.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Get Started ────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.rerun()

    # ── Join Waitlist ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("#### Join the Waitlist")
        st.caption("Be the first to know when we launch for your industry.")
        with st.form("waitlist_form", clear_on_submit=True):
            email = st.text_input("Email address", placeholder="you@company.com")
            submitted = st.form_submit_button("Join Waitlist", type="primary", use_container_width=True)
            if submitted:
                if not email or "@" not in email or "." not in email.split("@")[-1]:
                    st.error("Please enter a valid email address.")
                else:
                    ok, msg = save_waitlist_email(email.strip())
                    (st.success if ok else st.error)(msg)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP  (shown when authenticated)
# ══════════════════════════════════════════════════════════════════════════════
def show_app():
    # Sidebar
    with st.sidebar:
        if st.button("← Back to home", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.rerun()
        st.divider()

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

        env_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not env_key:
            api_key = st.text_input("Anthropic API Key", type="password",
                                    help="Set ANTHROPIC_API_KEY in Railway to skip this")
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
        else:
            st.success("API key loaded", icon="✓")

        st.divider()
        st.caption("Steps 01–04 · The Résumé Loop")

    # Helpers
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

    def stream_response(system_prompt, user_message, placeholder):
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

    st.title("🎯 JobPA — Beat the ATS")
    st.caption("The Résumé Loop: Diagnose → Refine → Rewrite → Prep")

    tab1, tab2, tab3, tab4 = st.tabs(["01 · Diagnose", "02 · Refine", "03 · Rewrite", "04 · Prep"])

    # ── 01 Diagnose ───────────────────────────────────────────────────────────
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
                final, _ = stream_response(DIAGNOSE_PROMPT,
                    f"Please run a full ATS diagnostic on this résumé:\n\n{cv_text}", output)
            st.caption(f"Tokens — input: {final.usage.input_tokens} / output: {final.usage.output_tokens}")

    # ── 02 Refine ─────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("Keyword Gap Analysis")
        st.caption("Run your CV against a real job description — surface exact keywords you're missing.")
        jd2 = st.text_area("Job Description", height=200,
                           placeholder="Paste the job description here…", key="jd2")
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
            with st.spinner("Analysing gap…"):
                final, _ = stream_response(REFINE_PROMPT,
                    f"## My CV\n\n{cv_text}\n\n---\n\n## Job Description\n\n{jd2}", output)
            st.caption(f"Tokens — input: {final.usage.input_tokens} / output: {final.usage.output_tokens}")

    # ── 03 Rewrite ────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("XYZ Bullet Rewriter")
        st.caption("Accomplished **X**, as measured by **Y**, by doing **Z**.")
        jd3 = st.text_area("Job Description (optional)", height=150,
                           placeholder="Paste a job description to focus the rewrites, or leave blank…", key="jd3")
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
5. End with ## METRIC GAPS listing all placeholders.
"""
            user_msg = f"## CV\n\n{cv_text}"
            if jd3.strip():
                user_msg += f"\n\n---\n\n## Target Job Description\n\n{jd3}"
            user_msg += "\n\nPlease rewrite every experience bullet using the XYZ formula."
            with st.spinner("Rewriting…"):
                final, _ = stream_response(REWRITE_PROMPT, user_msg, output)
            st.caption(f"Tokens — input: {final.usage.input_tokens} / output: {final.usage.output_tokens}")

    # ── 04 Prep ───────────────────────────────────────────────────────────────
    with tab4:
        st.subheader("Interview Simulator")
        st.caption("The hardest questions in your field — every answer scored /10.")
        col1, col2 = st.columns([3, 1])
        with col1:
            jd4 = st.text_area("Job Description (optional)", height=120,
                               placeholder="Paste a JD to get role-specific questions…", key="jd4")
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
            for msg in st.session_state.interview_messages[1:]:
                with st.chat_message("user" if msg["role"] == "user" else "assistant"):
                    st.markdown(msg["content"])

            last_role = st.session_state.interview_messages[-1]["role"] if st.session_state.interview_messages else None
            if last_role == "user":
                with st.chat_message("assistant"):
                    placeholder = st.empty()
                    client = get_client()
                    full = ""
                    with client.messages.stream(
                        model="claude-opus-4-6", max_tokens=1024, system=PREP_SYSTEM,
                        messages=st.session_state.interview_messages,
                    ) as stream:
                        for text in stream.text_stream:
                            full += text
                            placeholder.markdown(full + "▌")
                    placeholder.markdown(full)
                    st.session_state.interview_messages.append({"role": "assistant", "content": full})
                    st.session_state.interview_round += 1
                    if st.session_state.interview_round >= st.session_state.interview_rounds:
                        st.session_state.interview_messages.append({
                            "role": "user",
                            "content": "The interview is complete. Please provide the final INTERVIEW SUMMARY.",
                        })
                        st.session_state.interview_active = False
                        st.rerun()

            if st.session_state.interview_active and st.session_state.interview_messages[-1]["role"] == "assistant":
                answer = st.chat_input("Your answer…")
                if answer:
                    st.session_state.interview_messages.append({"role": "user", "content": answer})
                    st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.authenticated:
    show_app()
else:
    show_landing()
