from __future__ import annotations

import streamlit as st

import auth
from db import delete_opportunity, get_opportunities
from utils import render_section_title


st.set_page_config(page_title="Delete Opportunity", page_icon="🗑️", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("Delete Opportunity")
    render_section_title("Remove a record", "Admin users can delete an opportunity after reviewing its details.")

    if not auth.require_admin():
        return

    try:
        records = get_opportunities(limit=500, sort_by="created_at", sort_order="DESC")
    except Exception as exc:
        st.error(f"Unable to fetch opportunities: {exc}")
        return

    if records.empty:
        st.info("No records available for deletion.")
        return

    selection = st.selectbox(
        "Select an opportunity to delete",
        records["opportunity_id"].tolist(),
        format_func=lambda opportunity_id: f"#{opportunity_id} - {records.loc[records['opportunity_id'] == opportunity_id, 'company_name'].iloc[0]} | {records.loc[records['opportunity_id'] == opportunity_id, 'job_title'].iloc[0]}",
    )
    record = records.loc[records["opportunity_id"] == selection]
    st.dataframe(record, use_container_width=True, hide_index=True)

    confirm = st.checkbox("I understand that deleting this record is permanent.")
    if st.button("Delete Record", type="primary", use_container_width=True, disabled=not confirm):
        try:
            deleted = delete_opportunity(int(selection))
            if deleted:
                st.success("Record deleted successfully.")
                st.rerun()
            else:
                st.warning("The record was not found or had already been deleted.")
        except Exception as exc:
            st.error(f"Deletion failed: {exc}")


if __name__ == "__main__":
    main()
