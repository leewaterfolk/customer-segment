import streamlit as st


def google_login_available() -> bool:
    if not hasattr(st, "login"):
        return False
    try:
        return "auth" in st.secrets
    except Exception:
        return False


def current_user() -> dict | None:
    """Returns {"email": ..., "name": ...} if logged in via Google, else None."""
    try:
        if hasattr(st.user, "is_logged_in") and st.user.is_logged_in:
            return {
                "email": getattr(st.user, "email", "") or "",
                "name": getattr(st.user, "name", "") or "",
            }
    except Exception:
        pass
    return None


def require_auth():
    """Call at top of each page. Redirects to landing if not authenticated."""
    if not st.session_state.get("authenticated"):
        st.switch_page("app.py")
        st.stop()
