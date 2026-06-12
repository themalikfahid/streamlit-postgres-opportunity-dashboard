from __future__ import annotations

import streamlit as st

import auth
from db import get_opportunities, update_opportunity
from utils import CURRENCY_OPTIONS, EXPERIENCE_LEVEL_OPTIONS, STATUS_OPTIONS, WORK_MODE_OPTIONS, render_section_title, validate_opportunity_payload


st.set_page_config(page_title="Update Opportunity", page_icon="✏️", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("Update Opportunity")
    render_section_title("Modify an existing record", "Admin users can update status, salary, skills, deadline, and work mode.")

    if not auth.require_admin():
        return

    try:
        records = get_opportunities(limit=500, sort_by="created_at", sort_order="DESC")
    except Exception as exc:
        st.error(f"Unable to fetch opportunities: {exc}")
        return

    if records.empty:
        st.info("No records available for updates.")
        return

    selection = st.selectbox(
        "Choose an opportunity",
        records["opportunity_id"].tolist(),
        format_func=lambda opportunity_id: f"#{opportunity_id} - {records.loc[records['opportunity_id'] == opportunity_id, 'company_name'].iloc[0]} | {records.loc[records['opportunity_id'] == opportunity_id, 'job_title'].iloc[0]}",
    )
    current = records.loc[records["opportunity_id"] == selection].iloc[0]

    st.dataframe(current.to_frame().T, use_container_width=True, hide_index=True)

    with st.form("update_form"):
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current["status"]) if current["status"] in STATUS_OPTIONS else 0)
            work_mode = st.selectbox("Work Mode", WORK_MODE_OPTIONS, index=WORK_MODE_OPTIONS.index(current["work_mode"]) if current["work_mode"] in WORK_MODE_OPTIONS else 0)
            experience_level = st.selectbox("Experience Level", EXPERIENCE_LEVEL_OPTIONS, index=EXPERIENCE_LEVEL_OPTIONS.index(current["experience_level"]) if current["experience_level"] in EXPERIENCE_LEVEL_OPTIONS else 0)
            source_link = st.text_input("Source Link", value=str(current["source_link"]))
        with col2:
            salary_min = st.number_input("Salary Min", min_value=0.0, value=float(current["salary_min"]), step=100.0)
            salary_max = st.number_input("Salary Max", min_value=0.0, value=float(current["salary_max"]), step=100.0)
            required_skills = st.text_area("Required Skills", value=str(current["required_skills"]))
            application_deadline = st.date_input("Application Deadline")
        submitted = st.form_submit_button("Update Record", use_container_width=True)

    if submitted:
        payload = {
            "company_name": current["company_name"],
            "job_title": current["job_title"],
            "category": current["category"],
            "city": current["city"],
            "country": current["country"],
            "work_mode": work_mode,
            "required_skills": required_skills,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "currency": current["currency"],
            "experience_level": experience_level,
            "application_deadline": application_deadline,
            "status": status,
            "source_link": source_link,
        }
        cleaned, errors = validate_opportunity_payload(payload)
        if errors:
            st.error("\n".join(errors))
            return
        updates = {
            "work_mode": cleaned["work_mode"],
            "required_skills": cleaned["required_skills"],
            "salary_min": cleaned["salary_min"],
            "salary_max": cleaned["salary_max"],
            "experience_level": cleaned["experience_level"],
            "application_deadline": cleaned["application_deadline"],
            "status": cleaned["status"],
            "source_link": cleaned["source_link"],
        }
        try:
            updated = update_opportunity(int(selection), updates)
            if updated:
                st.success("Opportunity updated successfully.")
            else:
                st.warning("No changes were applied.")
        except Exception as exc:
            st.error(f"Update failed: {exc}")


if __name__ == "__main__":
    main()
