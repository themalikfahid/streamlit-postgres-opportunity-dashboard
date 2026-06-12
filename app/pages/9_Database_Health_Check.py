from __future__ import annotations

import streamlit as st

import auth
from db import get_opportunities, get_postgres_version, get_table_structure
from utils import render_section_title


st.set_page_config(page_title="Database Health Check", page_icon="🩺", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("Database Health Check")
    render_section_title("PostgreSQL diagnostics", "Review version details, row counts, latest data, and table structure.")

    try:
        version = get_postgres_version()
        records = get_opportunities(limit=1, sort_by="created_at", sort_order="DESC")
        structure = get_table_structure()
        total_rows = len(get_opportunities(limit=10000))
    except Exception as exc:
        st.error(f"Unable to inspect the database: {exc}")
        return

    metric_cols = st.columns(3)
    metric_cols[0].metric("Row Count", total_rows)
    metric_cols[1].metric("Version", "Available")
    metric_cols[2].metric("Latest Record", "Loaded" if not records.empty else "None")

    st.code(version)

    if not records.empty:
        st.subheader("Latest Record")
        st.dataframe(records, use_container_width=True, hide_index=True)

    st.subheader("Table Structure")
    st.dataframe(structure, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
