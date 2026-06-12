from __future__ import annotations

import hashlib
from typing import Dict

import streamlit as st


USER_STORE: Dict[str, Dict[str, str]] = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode("utf-8")).hexdigest(),
        "role": "admin",
        "display_name": "Administrator",
    },
    "viewer": {
        "password_hash": hashlib.sha256("viewer123".encode("utf-8")).hexdigest(),
        "role": "viewer",
        "display_name": "Viewer",
    },
}


def init_session_state() -> None:
    defaults = {
        "authenticated": False,
        "username": "",
        "role": "viewer",
        "display_name": "Guest",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def authenticate(username: str, password: str) -> bool:
    user = USER_STORE.get(username.strip().lower())
    if not user:
        return False
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if password_hash != user["password_hash"]:
        return False
    st.session_state["authenticated"] = True
    st.session_state["username"] = username.strip().lower()
    st.session_state["role"] = user["role"]
    st.session_state["display_name"] = user["display_name"]
    return True


def logout() -> None:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = "viewer"
    st.session_state["display_name"] = "Guest"


def current_user() -> Dict[str, str]:
    init_session_state()
    return {
        "authenticated": str(st.session_state.get("authenticated", False)),
        "username": str(st.session_state.get("username", "")),
        "role": str(st.session_state.get("role", "viewer")),
        "display_name": str(st.session_state.get("display_name", "Guest")),
    }


def is_admin() -> bool:
    init_session_state()
    return bool(st.session_state.get("authenticated")) and st.session_state.get("role") == "admin"


def is_authenticated() -> bool:
    init_session_state()
    return bool(st.session_state.get("authenticated"))


def require_admin() -> bool:
    if not is_admin():
        st.error("Admin access is required for this action.")
        return False
    return True


def require_login() -> bool:
    if not is_authenticated():
        st.error("Please log in to access the dashboard.")
        return False
    return True


def render_login_panel() -> None:
    init_session_state()
    if is_authenticated():
        st.sidebar.success(f"Signed in as {st.session_state['display_name']}")
        if st.sidebar.button("Logout", use_container_width=True):
            logout()
            st.rerun()
        return

    st.sidebar.markdown("### Sign in")
    with st.sidebar.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="admin or viewer")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if authenticate(username, password):
            st.sidebar.success("Authentication successful.")
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")


def render_access_banner() -> None:
    init_session_state()
    if is_authenticated():
        st.caption(f"Signed in as {st.session_state['display_name']} ({st.session_state['role']})")
    else:
        st.caption("Read-only preview until you sign in.")
