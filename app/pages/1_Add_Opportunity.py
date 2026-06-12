from __future__ import annotations

from datetime import date

import streamlit as st

import auth
from db import create_opportunity
from utils import CURRENCY_OPTIONS, CATEGORY_OPTIONS, EXPERIENCE_LEVEL_OPTIONS, STATUS_OPTIONS, WORK_MODE_OPTIONS, render_section_title, validate_opportunity_payload


st.set_page_config(page_title="Add Opportunity", page_icon="➕", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("Add Opportunity")
    render_section_title("Create a new opportunity record", "Admin users can insert validated job and internship opportunities into PostgreSQL.")

    if not auth.require_admin():
        st.info("Viewer accounts can explore the dashboard but cannot modify records.")
        return

    with st.form("add_opportunity_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            company_name = st.text_input("Company Name")
            job_title = st.text_input("Job Title")
            category = st.selectbox("Category", CATEGORY_OPTIONS)
            city = st.text_input("City")
            country = st.text_input("Country")
            work_mode = st.selectbox("Work Mode", WORK_MODE_OPTIONS)
            required_skills = st.text_area("Required Skills", placeholder="Python, SQL, Power BI")
        with right:
            salary_min = st.number_input("Salary Min", min_value=0.0, step=100.0)
            salary_max = st.number_input("Salary Max", min_value=0.0, step=100.0)
            currency = st.selectbox("Currency", CURRENCY_OPTIONS)
            experience_level = st.selectbox("Experience Level", EXPERIENCE_LEVEL_OPTIONS)
            application_deadline = st.date_input("Application Deadline", value=date.today())
            status = st.selectbox("Status", STATUS_OPTIONS)
            source_link = st.text_input("Source Link")
        submitted = st.form_submit_button("Save Opportunity", use_container_width=True)

    if submitted:
        payload = {
            "company_name": company_name,
            "job_title": job_title,
            "category": category,
            "city": city,
            "country": country,
            "work_mode": work_mode,
            "required_skills": required_skills,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "currency": currency,
            "experience_level": experience_level,
            "application_deadline": application_deadline,
            "status": status,
            "source_link": source_link,
        }
        cleaned, errors = validate_opportunity_payload(payload)
        if errors:
            st.error("\n".join(errors))
            return
        try:
            inserted_id = create_opportunity(cleaned)
            st.success(f"Opportunity created successfully with ID {inserted_id}.")
        except Exception as exc:
            st.error(f"Unable to save record: {exc}")


if __name__ == "__main__":
    main()
