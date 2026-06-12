from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

import auth
from db import count_opportunities, get_opportunities
from utils import deadline_bucket_frame, render_section_title, top_skills_frame


st.set_page_config(page_title="Analytics Dashboard", page_icon="📈", layout="wide")


def metric_card(label: str, value: object) -> None:
    st.metric(label, value)


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("Analytics Dashboard")
    render_section_title("Operational insights", "A quick snapshot of the opportunity dataset.")

    try:
        df = get_opportunities(limit=5000, sort_by="created_at", sort_order="DESC")
    except Exception as exc:
        st.error(f"Unable to load analytics data: {exc}")
        return

    total = len(df)
    open_jobs = int((df["status"].astype(str).str.lower() == "open").sum()) if total else 0
    closed_jobs = int(df["status"].astype(str).str.lower().isin(["closed", "expired", "archived"]).sum()) if total else 0
    remote_jobs = int((df["work_mode"].astype(str).str.lower() == "remote").sum()) if total else 0
    hybrid_jobs = int((df["work_mode"].astype(str).str.lower() == "hybrid").sum()) if total else 0
    total_companies = int(df["company_name"].nunique()) if total else 0

    kpi_cols = st.columns(6)
    kpi_cols[0].metric("Total Opportunities", total)
    kpi_cols[1].metric("Open Jobs", open_jobs)
    kpi_cols[2].metric("Closed Jobs", closed_jobs)
    kpi_cols[3].metric("Remote Jobs", remote_jobs)
    kpi_cols[4].metric("Hybrid Jobs", hybrid_jobs)
    kpi_cols[5].metric("Total Companies", total_companies)

    if total == 0:
        st.info("No data available for analytics.")
        return

    category_counts = df["category"].value_counts().reset_index()
    category_counts.columns = ["category", "count"]
    work_mode_counts = df["work_mode"].value_counts().reset_index()
    work_mode_counts.columns = ["work_mode", "count"]
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    salary_df = df.copy()
    salary_df["average_salary"] = (salary_df["salary_min"].astype(float) + salary_df["salary_max"].astype(float)) / 2
    skills_df = top_skills_frame(df)
    deadline_df = deadline_bucket_frame(df)

    chart1, chart2 = st.columns(2)
    with chart1:
        fig = px.bar(category_counts, x="category", y="count", title="Category Distribution", color="category")
        st.plotly_chart(fig, use_container_width=True)
    with chart2:
        fig = px.pie(work_mode_counts, names="work_mode", values="count", title="Work Mode Distribution", hole=0.35)
        st.plotly_chart(fig, use_container_width=True)

    chart3, chart4 = st.columns(2)
    with chart3:
        fig = px.bar(status_counts, x="status", y="count", title="Status Distribution", color="status")
        st.plotly_chart(fig, use_container_width=True)
    with chart4:
        fig = px.box(salary_df, y="average_salary", x="category", title="Salary Analysis", points="all")
        st.plotly_chart(fig, use_container_width=True)

    chart5, chart6 = st.columns(2)
    with chart5:
        if not skills_df.empty:
            fig = px.bar(skills_df, x="skill", y="count", title="Top Skills Analysis", color="count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No skills data available.")
    with chart6:
        if not deadline_df.empty:
            fig = px.line(deadline_df, x="deadline", y="count", title="Deadline Trends", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No deadline trend data available.")


if __name__ == "__main__":
    main()
