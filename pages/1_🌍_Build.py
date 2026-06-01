import streamlit as st
from lib.auth import require_auth
from lib.claude_client import stream_claude
from lib.regions import REGIONS, REGION_ORDER, build_prompt

st.set_page_config(page_title="Build — JobPA", page_icon="🌍", layout="wide")
require_auth()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.page_link("app.py", label="← Home", icon="🏠")
    if st.session_state.get("user_email"):
        st.caption(f"👤 {st.session_state.user_email}")
    st.divider()
    cv = st.text_area("Your CV / background", height=320,
                      placeholder="Paste any existing résumé (any format/language), "
                                  "or bullet-list your experience, skills, education.",
                      key="cv_global")
    st.caption("This CV is shared across all tabs.")

# ── Main ─────────────────────────────────────────────────────────────────────
st.title("🌍 Region-Ready Résumé Builder")
st.caption("A résumé that wins in Seoul gets auto-rejected in San Francisco. We fix that.")

c1, c2 = st.columns([1, 1])
with c1:
    region_key = st.selectbox(
        "Target market",
        REGION_ORDER,
        format_func=lambda k: REGIONS[k]["label"],
    )
with c2:
    role = st.text_input("Target role (optional)", placeholder="e.g. Product Manager")

r = REGIONS[region_key]

# Region explainer
cols = st.columns(4)
pills = [
    ("📄", "Document", r["doc"]),
    ("🌐", "Language", r["lang"]),
    ("📷", "Photo", "Required" if "never" not in r["photo"].lower() and "no" not in r["photo"][:4].lower() else "Not included"),
    ("📏", "Length", r["length"]),
]
for col, (icon, label, val) in zip(cols, pills):
    col.metric(f"{icon} {label}", val)

with st.expander("Full regional rules for " + r["label"]):
    st.markdown(f"""
**Photo:** {r["photo"]}

**Personal details:** {r["personal"]}

**Required sections:**
""" + "\n".join(f"- {s}" for s in r["sections"]) + f"""

**Cover letter / self-intro:** {r["cover"]}

**Tone:** {r["tone"]}

**Avoid:** {r["avoid"]}

**ATS / portals:** {r["ats"]}
""")

st.divider()

if st.button(f"Build my {r['doc']}", type="primary", key="btn_build"):
    if not cv.strip():
        st.warning("Add your CV or background info in the sidebar first.")
        st.stop()
    out = st.empty()
    msg = f"## Candidate's background / existing résumé\n\n{cv}"
    if role.strip():
        msg += f"\n\n## Target role\n\n{role.strip()}"
    msg += f"\n\nProduce a fully localised {r['doc']} for the {r['label']} market."
    with st.spinner(f"Localising for {r['label']}…"):
        final = stream_claude(build_prompt(region_key), msg, out)
    st.caption(f"Tokens — in: {final.usage.input_tokens} / out: {final.usage.output_tokens}")
