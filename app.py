"""
JobPA — Beat the ATS
Landing page + auth router.

Env / Secrets required:
  ANTHROPIC_API_KEY  (required)

Optional Google login — add to Streamlit secrets:
  [auth]
  redirect_uri    = "https://suminleekorea.streamlit.app/oauth2callback"
  cookie_secret   = "<random 32-char string>"
  client_id       = "<google-oauth-client-id>"
  client_secret   = "<google-oauth-client-secret>"
  server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

  Then add the same redirect_uri to Google Cloud Console →
  Credentials → OAuth client → Authorised redirect URIs.
"""

import os
import streamlit as st
from lib.auth import google_login_available, current_user

st.set_page_config(
    page_title="JobPA — Beat the ATS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Sync Google session → session_state ──────────────────────────────────────
user = current_user()
if user:
    st.session_state.authenticated = True
    st.session_state.user_email = user["email"]
    st.session_state.user_name = user.get("name", "")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None

# ── If already authenticated, go straight to app ────────────────────────────
if st.session_state.authenticated:
    st.switch_page("pages/1_🌍_Build.py")

# ════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem; max-width: 960px; }

  .hero { text-align: center; padding: 64px 20px 48px; }
  .hero h1 { font-size: 3.6rem; font-weight: 900; letter-spacing: -2px;
              background: linear-gradient(135deg, #fff 40%, #e94560);
              -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .hero .sub { font-size: 1.25rem; color: #888; margin: 12px 0 48px; }

  .loop-grid { display: grid; grid-template-columns: repeat(5, 1fr);
               gap: 12px; max-width: 900px; margin: 0 auto 56px; }
  .loop-card { background: #111118; border: 1px solid #1e1e2e;
               border-radius: 14px; padding: 24px 16px; text-align: center;
               transition: border-color .2s; }
  .loop-card:hover { border-color: #e94560; }
  .loop-num  { font-size: 1.8rem; font-weight: 900; color: #e94560; }
  .loop-icon { font-size: 1.6rem; margin: 6px 0; }
  .loop-title{ font-size: .95rem; font-weight: 700; margin-bottom: 6px; }
  .loop-desc { font-size: .78rem; color: #666; line-height: 1.5; }

  .divider { border: none; border-top: 1px solid #1e1e2e; margin: 48px 0 32px; }

  .waitlist-wrap { max-width: 420px; margin: 0 auto; text-align: center; }
  .waitlist-wrap h3 { font-size: 1.1rem; margin-bottom: 4px; }
  .waitlist-wrap p { color: #666; font-size: .9rem; margin-bottom: 20px; }
</style>

<div class="hero">
  <h1>Beat the ATS.</h1>
  <div class="sub">The Résumé Loop — build region-ready, then go from invisible to interview-ready.</div>

  <div class="loop-grid">
    <div class="loop-card">
      <div class="loop-num">00</div>
      <div class="loop-icon">🌍</div>
      <div class="loop-title">Build</div>
      <div class="loop-desc">Region-native résumé for Korea, US, SG, France, UK, Germany</div>
    </div>
    <div class="loop-card">
      <div class="loop-num">01</div>
      <div class="loop-icon">🔍</div>
      <div class="loop-title">Diagnose</div>
      <div class="loop-desc">ATS parse score, auto-reject triggers, top 5 quick wins</div>
    </div>
    <div class="loop-card">
      <div class="loop-num">02</div>
      <div class="loop-icon">🎯</div>
      <div class="loop-title">Refine</div>
      <div class="loop-desc">Surface exact keywords missing vs the job description</div>
    </div>
    <div class="loop-card">
      <div class="loop-num">03</div>
      <div class="loop-icon">✏️</div>
      <div class="loop-title">Rewrite</div>
      <div class="loop-desc">Every bullet → XYZ formula with quantified impact</div>
    </div>
    <div class="loop-card">
      <div class="loop-num">04</div>
      <div class="loop-icon">💬</div>
      <div class="loop-title">Prep</div>
      <div class="loop-desc">AI hiring manager · hardest questions · scored /10</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── CTA buttons ──────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 1.6, 1])
with c2:
    if google_login_available():
        if st.button("Continue with Google", type="primary", use_container_width=True):
            st.login("google")
        st.markdown("<div style='text-align:center;color:#555;font-size:.85rem;margin:8px 0'>or</div>",
                    unsafe_allow_html=True)
        if st.button("Try it now — no login", use_container_width=True):
            st.session_state.authenticated = True
            st.rerun()
    else:
        if st.button("🚀  Get Started", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.rerun()

# ── Waitlist ─────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
w1, w2, w3 = st.columns([1, 1.4, 1])
with w2:
    st.markdown("""
<div class="waitlist-wrap">
  <h3>Join the Waitlist</h3>
  <p>Be the first to know when we launch for your industry.</p>
</div>
""", unsafe_allow_html=True)
    with st.form("waitlist", clear_on_submit=True):
        email = st.text_input("", placeholder="your@email.com", label_visibility="collapsed")
        if st.form_submit_button("Join Waitlist", type="primary", use_container_width=True):
            if not email or "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            else:
                endpoint = os.environ.get("WAITLIST_ENDPOINT", "")
                if endpoint:
                    try:
                        import urllib.request, json
                        req = urllib.request.Request(
                            endpoint,
                            data=json.dumps({"email": email.strip()}).encode(),
                            headers={"Content-Type": "application/json"},
                        )
                        urllib.request.urlopen(req, timeout=10)
                        st.success("You're on the list! We'll be in touch.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    with open("waitlist.txt", "a") as f:
                        f.write(email.strip() + "\n")
                    st.success("You're on the list!")
