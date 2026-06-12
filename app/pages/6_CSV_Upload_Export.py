# CSV Upload & Export module - Haseeb
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
    render_section_title(
        "Bulk ingest and download records",
        "Upload validated CSV files or export the current filtered dataset."
    )

    tab_upload, tab_export = st.tabs(["Upload CSV", "Export CSV"])

    # ---- Upload Tab ----
    with tab_upload:
        if not auth.require_admin():
            st.info("CSV bulk insert is limited to admin users.")

        csv_file = st.file_uploader("Upload a CSV file", type=["csv"])

        if csv_file is not None:
            try:
                raw_df = pd.read_csv(csv_file)

                st.subheader("Preview")
                st.dataframe(raw_df.head(10), use_container_width=True, hide_index=True)

                clean_df, validation_errors = validate_csv_dataframe(raw_df)

                if validation_errors:
                    st.error("\n".join(validation_errors))
                else:
                    if st.button("Insert Valid Records", use_container_width=True):
                        insert_result = bulk_insert(clean_df.to_dict(orient="records"))
                        st.success(
                            f"Inserted {insert_result['inserted']} of {insert_result['total']} rows. "
                            f"Skipped {insert_result['skipped']} duplicates."
                        )

            except Exception as exc:
                st.error(f"Unable to process the uploaded file: {exc}")

    # ---- Export Tab ----
    with tab_export:
        export_filters = {}
        search_term = st.text_input("Search filtered export", placeholder="Optional search term")

        if search_term:
            export_filters["search"] = search_term

        try:
            export_df = get_opportunities(
                filters=export_filters,
                limit=5000,
                sort_by="created_at",
                sort_order="DESC"
            )
        except Exception as exc:
            st.error(f"Unable to load export data: {exc}")
            return

        st.dataframe(export_df.head(100), use_container_width=True, hide_index=True)

        buffer = StringIO()
        export_df.to_csv(buffer, index=False)

        st.download_button(
            label="Download CSV",
            data=buffer.getvalue(),
            file_name="opportunities_export.csv",
            mime="text/csv",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
