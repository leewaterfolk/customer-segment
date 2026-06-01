import streamlit as st
from lib.auth import require_auth
from lib.claude_client import stream_claude

st.set_page_config(page_title="Diagnose — JobPA", page_icon="🔍", layout="wide")
require_auth()

with st.sidebar:
    st.page_link("app.py", label="← Home", icon="🏠")
    if st.session_state.get("user_email"):
        st.caption(f"👤 {st.session_state.user_email}")
    st.divider()
    cv = st.text_area("Your CV", height=380,
                      placeholder="Paste your CV here…",
                      key="cv_global")

st.title("🔍 ATS Diagnostic")
st.caption("See your résumé the way an ATS parses it — catch every auto-reject trigger before you apply.")

SYSTEM = """\
You are an ATS (Applicant Tracking System) expert. Analyse the résumé exactly as a
modern ATS would, then give clear actionable feedback.

## ATS PARSE SCORE  /100
Overall ATS compatibility score. 2–3 line justification.

## AUTO-REJECT TRIGGERS
Elements that cause instant auto-rejection.
Format each: "⚠ [Issue] — [Why it matters / how to fix]"
If none found: "✓ No auto-reject triggers detected."

## KEYWORD DENSITY
Top 10 keywords present in the CV (with approximate frequency).
Then: 3–5 generic filler phrases that dilute signal — list them and suggest removals.

## SECTION HEALTH
Score each section: Contact Info / Summary / Work Experience / Education / Skills /
Certifications — (✅ Strong / ⚠ Weak / ❌ Missing) with a one-line note.

## TOP 5 QUICK WINS
Concrete changes ordered by ATS impact.
Format: "1. [Action] → [Expected gain]"
"""

if st.button("Run ATS Diagnostic", type="primary"):
    if not cv.strip():
        st.warning("Paste your CV in the sidebar first.")
        st.stop()
    out = st.empty()
    with st.spinner("Analysing…"):
        final = stream_claude(SYSTEM, f"Run a full ATS diagnostic:\n\n{cv}", out)
    st.caption(f"Tokens — in: {final.usage.input_tokens} / out: {final.usage.output_tokens}")
