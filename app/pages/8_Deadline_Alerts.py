from __future__ import annotations

import streamlit as st

import auth
from db import get_deadline_alerts, get_expired_jobs
from utils import render_section_title


st.set_page_config(page_title="Deadline Alerts", page_icon="⏰", layout="wide")


def main() -> None:
    auth.init_session_state()
    auth.render_login_panel()
    st.title("Deadline Alerts")
    render_section_title("Upcoming and expired opportunities", "Monitor jobs closing soon and records that have already expired.")

    upcoming = get_deadline_alerts(days=7)
    expired = get_expired_jobs()

    left, right = st.columns(2)
    with left:
        st.subheader("Closing within 7 days")
        if upcoming.empty:
            st.info("No deadlines closing within the next 7 days.")
        else:
            st.dataframe(upcoming, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Expired jobs")
        if expired.empty:
            st.info("No expired jobs found.")
        else:
            st.dataframe(expired, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
