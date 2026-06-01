import streamlit as st
from lib.auth import require_auth
from lib.claude_client import stream_claude

st.set_page_config(page_title="Refine — JobPA", page_icon="🎯", layout="wide")
require_auth()

with st.sidebar:
    st.page_link("app.py", label="← Home", icon="🏠")
    if st.session_state.get("user_email"):
        st.caption(f"👤 {st.session_state.user_email}")
    st.divider()
    cv = st.text_area("Your CV", height=340,
                      placeholder="Paste your CV here…",
                      key="cv_global")

st.title("🎯 Keyword Gap Analysis")
st.caption("Run your CV against a real job description — surface the exact keywords you're missing.")

jd = st.text_area("Job Description", height=220,
                  placeholder="Paste the full job description here…")

SYSTEM = """\
You are an expert career coach specialised in ATS keyword optimisation.
Given a CV and job description, produce:

## MATCH SCORE  /100
How well the CV matches this specific JD. 2-line rationale.

## TAILORED BULLETS TO EMPHASISE
5–8 existing achievements from the CV that best match this role.
Rewrite each as a punchy, metric-driven, ATS-optimised bullet.
Format: "• [Original] → [Tailored version]"

## MISSING KEYWORDS & GAPS
Keywords, tools, frameworks, certifications in the JD that are absent or
under-represented in the CV.
Format: "• [Keyword] — [How to surface it: add project / certify / reframe existing experience]"

## QUICK ACTION LIST
Top 3 changes to make RIGHT NOW to maximise interview chances for this role.
"""

if st.button("Analyse Gap", type="primary"):
    if not cv.strip():
        st.warning("Paste your CV in the sidebar first.")
        st.stop()
    if not jd.strip():
        st.warning("Paste the job description above.")
        st.stop()
    out = st.empty()
    with st.spinner("Analysing…"):
        final = stream_claude(SYSTEM, f"## CV\n\n{cv}\n\n---\n\n## Job Description\n\n{jd}", out)
    st.caption(f"Tokens — in: {final.usage.input_tokens} / out: {final.usage.output_tokens}")
