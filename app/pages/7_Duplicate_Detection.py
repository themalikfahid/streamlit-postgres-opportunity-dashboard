# Duplicate Detection module - Updated by Haseeb
from __future__ import annotations

import streamlit as st

import auth
from db import duplicate_check
from utils import render_section_title

st.set_page_config(page_title="Duplicate Detection", page_icon="🧬", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()

    st.title("Duplicate Detection")
    render_section_title(
        "Find repeated opportunity records",
        "Duplicates are grouped by company, title, city, and source link."
    )

    try:
        duplicate_groups = duplicate_check()
    except Exception as exc:
        st.error(f"Unable to inspect duplicates: {exc}")
        return

    if duplicate_groups.empty:
        st.success("No duplicate groups were found.")
    else:
        st.warning(f"Found {len(duplicate_groups)} duplicate groups.")
        st.dataframe(duplicate_groups, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
