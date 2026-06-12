from __future__ import annotations

from io import StringIO

import pandas as pd
import streamlit as st

import auth
from db import bulk_insert, get_opportunities
from utils import render_section_title, validate_csv_dataframe


st.set_page_config(page_title="CSV Upload & Export", page_icon="📤", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("CSV Upload & Export")
    render_section_title("Bulk ingest and download records", "Upload validated CSV files or export the current filtered dataset.")

    upload_tabs = st.tabs(["Upload CSV", "Export CSV"])

    with upload_tabs[0]:
        if not auth.require_admin():
            st.info("CSV bulk insert is limited to admin users.")
        uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                preview = df.head(10)
                st.subheader("Preview")
                st.dataframe(preview, use_container_width=True, hide_index=True)
                normalized, errors = validate_csv_dataframe(df)
                if errors:
                    st.error("\n".join(errors))
                else:
                    if st.button("Insert Valid Records", use_container_width=True):
                        result = bulk_insert(normalized.to_dict(orient="records"))
                        st.success(f"Inserted {result['inserted']} of {result['total']} rows. Skipped {result['skipped']} duplicates.")
            except Exception as exc:
                st.error(f"Unable to process the uploaded file: {exc}")

    with upload_tabs[1]:
        filters = {}
        search = st.text_input("Search filtered export", placeholder="Optional search term")
        if search:
            filters["search"] = search
        try:
            df = get_opportunities(filters=filters, limit=5000, sort_by="created_at", sort_order="DESC")
        except Exception as exc:
            st.error(f"Unable to load export data: {exc}")
            return

        st.dataframe(df.head(100), use_container_width=True, hide_index=True)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download CSV",
            data=csv_buffer.getvalue(),
            file_name="opportunities_export.csv",
            mime="text/csv",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
