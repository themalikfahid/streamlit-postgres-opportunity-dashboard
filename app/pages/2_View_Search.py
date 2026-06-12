from __future__ import annotations

import streamlit as st

import auth
from db import count_opportunities, get_opportunities
from utils import paginate_dataframe, render_section_title


st.set_page_config(page_title="View and Search", page_icon="🔎", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("View and Search")
    render_section_title("Browse the opportunity catalog", "Search, filter, and page through records stored in PostgreSQL.")

    filters = {}
    search = st.text_input("Search", placeholder="Company, job title, skills, city, or status")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        filters["category"] = st.text_input("Category filter")
    with col2:
        filters["work_mode"] = st.text_input("Work mode filter")
    with col3:
        filters["status"] = st.text_input("Status filter")
    with col4:
        filters["city"] = st.text_input("City filter")

    page_size = st.selectbox("Rows per page", [5, 10, 15, 20], index=1)
    page = st.number_input("Page", min_value=1, value=1, step=1)

    filters = {key: value for key, value in filters.items() if value}
    if search:
        filters["search"] = search

    try:
        total_rows = count_opportunities(filters)
        records = get_opportunities(filters=filters, limit=page_size, offset=(page - 1) * page_size, sort_by="created_at", sort_order="DESC")
    except Exception as exc:
        st.error(f"Unable to load data: {exc}")
        return

    st.caption(f"{total_rows} matching records")
    st.dataframe(records, use_container_width=True, hide_index=True)

    if total_rows == 0:
        st.info("No records match the current filters.")
    elif (page - 1) * page_size >= total_rows:
        st.warning("The selected page is beyond the available records. Reduce the page number.")


if __name__ == "__main__":
    main()
