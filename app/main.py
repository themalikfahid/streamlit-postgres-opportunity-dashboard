from __future__ import annotations

import streamlit as st

import auth
from db import count_opportunities, get_engine
from utils import render_section_title


st.set_page_config(
    page_title="Internship & Job Opportunity Tracking Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(17, 24, 39, 0.1), transparent 28%),
                    radial-gradient(circle at top right, rgba(15, 118, 110, 0.12), transparent 24%),
                    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
            }
            .hero {
                padding: 2.2rem;
                border-radius: 24px;
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(148, 163, 184, 0.25);
                box-shadow: 0 20px 50px rgba(15, 23, 42, 0.08);
            }
            .hero h1 {
                margin-bottom: 0.4rem;
            }
            .pill {
                display: inline-block;
                padding: 0.35rem 0.75rem;
                margin-right: 0.45rem;
                margin-bottom: 0.45rem;
                border-radius: 999px;
                background: #0f766e;
                color: #ffffff;
                font-size: 0.82rem;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_home() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    apply_theme()

    st.markdown(
        """
        <div class="hero">
            <h1>Internship & Job Opportunity Tracking Dashboard</h1>
            <p>Track applications, inspect trends, manage deadlines, and maintain a clean PostgreSQL-backed opportunity catalog.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        get_engine()
        total_records = count_opportunities()
    except Exception:
        total_records = 0

    metric_columns = st.columns(4)
    metric_columns[0].metric("Stored Opportunities", total_records)
    metric_columns[1].metric("Authentication", st.session_state.get("role", "viewer").title())
    metric_columns[2].metric("Database", "PostgreSQL")
    metric_columns[3].metric("Interface", "Streamlit")

    st.write("")
    left, right = st.columns([1.2, 1])

    with left:
        render_section_title("Project Overview", "A complete university-grade data engineering dashboard.")
        st.markdown(
            """
            - Centralized storage in PostgreSQL.
            - Streamlit multipage experience for CRUD, analytics, CSV workflow, and health checks.
            - Role-based access for admin and viewer accounts.
            - Dockerized deployment with reproducible startup.
            """
        )

        st.markdown("### Quick Navigation")
        nav_columns = st.columns(3)
        nav_columns[0].page_link("pages/1_Add_Opportunity.py", label="Add Opportunity")
        nav_columns[1].page_link("pages/5_Analytics_Dashboard.py", label="Analytics Dashboard")
        nav_columns[2].page_link("pages/9_Database_Health_Check.py", label="DB Health Check")

    with right:
        render_section_title("Team Members", "Replace the sample names with your project team.")
        st.markdown(
            """
            - **Project Lead:** Aisha Khan
            - **Data Engineer:** Daniel Mensah
            - **Backend Developer:** Priya Patel
            - **BI / QA Analyst:** Omar Hassan
            """
        )

        render_section_title("Technology Stack", None)
        st.markdown(
            """
            <span class="pill">Streamlit</span>
            <span class="pill">PostgreSQL</span>
            <span class="pill">SQLAlchemy</span>
            <span class="pill">psycopg2</span>
            <span class="pill">Plotly</span>
            <span class="pill">Docker</span>
            <span class="pill">Pandas</span>
            """,
            unsafe_allow_html=True,
        )

    render_section_title("Architecture", "How the dashboard is wired end to end.")
    st.markdown(
        """
        1. The Streamlit UI collects user input and applies session-based authentication.
        2. The reusable database layer uses SQLAlchemy for query execution and psycopg2 for bulk operations.
        3. PostgreSQL stores the normalized opportunity records and serves as the single source of truth.
        4. Analytics pages transform the dataset into KPIs, charts, alerts, and health insights.
        5. Docker Compose starts PostgreSQL, pgAdmin, and the Streamlit app with one command.
        """
    )

    if not st.session_state.get("authenticated", False):
        st.info("Sign in from the sidebar to enable admin-only actions such as add, update, delete, and CSV bulk upload.")


if __name__ == "__main__":
    render_home()
