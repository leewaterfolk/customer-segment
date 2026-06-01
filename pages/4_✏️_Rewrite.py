import streamlit as st
from lib.auth import require_auth
from lib.claude_client import stream_claude

st.set_page_config(page_title="Rewrite — JobPA", page_icon="✏️", layout="wide")
require_auth()

with st.sidebar:
    st.page_link("app.py", label="← Home", icon="🏠")
    if st.session_state.get("user_email"):
        st.caption(f"👤 {st.session_state.user_email}")
    st.divider()
    cv = st.text_area("Your CV", height=340,
                      placeholder="Paste your CV here…",
                      key="cv_global")

st.title("✏️ XYZ Bullet Rewriter")
st.markdown("**Accomplished [X], as measured by [Y], by doing [Z].**")
st.caption("Every weak bullet rebuilt into a quantified, ATS-optimised achievement.")

jd = st.text_area("Job Description (optional — targets the rewrites)",
                  height=120,
                  placeholder="Paste a JD to focus the rewrites on the most relevant skills…")

SYSTEM = """\
You are an expert résumé writer specialised in the XYZ achievement formula:
"Accomplished [X], as measured by [Y], by doing [Z]."

Rewrite EVERY experience bullet in the CV using this formula.

Rules:
1. Never invent metrics. Where data is missing, write: [METRIC NEEDED: e.g. "% improvement / $ saved / N users"]
2. Use strong action verbs only. Delete "responsible for", "helped with", "assisted in".
3. If a JD is provided, prioritise language and skills from the JD.
4. Format each entry:
   ORIGINAL: <original bullet text>
   REWRITTEN: <XYZ version>
   (blank line between entries)
5. After all bullets, add:
   ## METRIC GAPS
   List every [METRIC NEEDED] placeholder — this is the candidate's homework to find real numbers.

Do not touch section headings, dates, education, or contact info.
"""

if st.button("Rewrite All Bullets", type="primary"):
    if not cv.strip():
        st.warning("Paste your CV in the sidebar first.")
        st.stop()
    out = st.empty()
    msg = f"## CV\n\n{cv}"
    if jd.strip():
        msg += f"\n\n---\n\n## Target Job Description\n\n{jd}"
    msg += "\n\nRewrite every experience bullet using the XYZ formula."
    with st.spinner("Rewriting…"):
        final = stream_claude(SYSTEM, msg, out, max_tokens=6000)
    st.caption(f"Tokens — in: {final.usage.input_tokens} / out: {final.usage.output_tokens}")
