# Internship & Job Opportunity Tracking Dashboard

A production-style Streamlit application for tracking internship and job opportunities with PostgreSQL, role-based authentication, analytics, CSV operations, duplicate detection, deadline alerts, and Dockerized deployment.

## Project Overview

This project is built for a university data engineering assignment and demonstrates a modular architecture that combines a Streamlit frontend with a PostgreSQL backend. The application stores opportunity records, supports CRUD operations, provides analytics, and offers operational health checks.

## Features

- Role-based authentication using Streamlit session state
- Admin and viewer accounts
- Add, view, search, update, and delete opportunities
- KPI cards and Plotly analytics dashboard
- CSV upload with validation and bulk insert
- CSV export for filtered records
- Duplicate detection logic
- Deadline alerts for upcoming and expired jobs
- PostgreSQL health check and table inspection
- Docker and Docker Compose deployment

## Folder Structure

```text
streamlit-postgres-opportunity-dashboard/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── queries.py
│   ├── auth.py
│   ├── utils.py
│   └── pages/
│       ├── 1_Add_Opportunity.py
│       ├── 2_View_Search.py
│       ├── 3_Update_Opportunity.py
│       ├── 4_Delete_Opportunity.py
│       ├── 5_Analytics_Dashboard.py
│       ├── 6_CSV_Upload_Export.py
│       ├── 7_Duplicate_Detection.py
│       ├── 8_Deadline_Alerts.py
│       └── 9_Database_Health_Check.py
├── database/
│   ├── init.sql
│   └── seed_data.sql
├── screenshots/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Authentication

Default credentials:

- Admin: `admin` / `admin123`
- Viewer: `viewer` / `viewer123`

Admin users can add, update, delete, and bulk upload data. Viewer users have read-only access.

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Description |
| --- | --- |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_HOST` | Database host name |
| `POSTGRES_PORT` | Database port |
| `PGADMIN_DEFAULT_EMAIL` | pgAdmin login email |
| `PGADMIN_DEFAULT_PASSWORD` | pgAdmin login password |
| `STREAMLIT_SERVER_PORT` | Streamlit port |

## PostgreSQL Setup

The database schema is defined in `database/init.sql`. The table is named `opportunities` and includes constraints for work mode, status, salary range, and unique source links.

The sample dataset in `database/seed_data.sql` inserts 40 realistic records.

## pgAdmin Setup

pgAdmin runs on port `5050` in Docker Compose.

1. Open `http://localhost:5050`.
2. Sign in using the email and password from `.env`.
3. Register a new server with:
   - Host: `postgres_db`
   - Port: `5432`
   - Maintenance database: `student_opportunities_db`
   - Username/password from your PostgreSQL environment variables

## How to Run

### Option 1: Docker Compose

```bash
docker compose up --build
```

Then open:

- Streamlit app: `http://localhost:8501`
- pgAdmin: `http://localhost:5050`
- PostgreSQL: `localhost:5432`

### Option 2: Local Python Environment

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Start PostgreSQL and apply `database/init.sql` and `database/seed_data.sql`.
4. Run:

```bash
streamlit run app/main.py
```

## Docker Commands

```bash
docker compose up --build
docker compose down
docker compose logs -f streamlit_app
docker compose logs -f postgres_db
```

## Screenshots

Add exported screenshots of the dashboard to the `screenshots/` folder. Suggested images:

- Home page
- Analytics dashboard
- CSV upload flow
- Deadline alerts
- Database health check

## Troubleshooting

- If the Streamlit app cannot connect to PostgreSQL, verify that the database container is healthy and the host name is `postgres_db` inside Docker.
- If pgAdmin cannot connect, confirm the server host, port, username, and password.
- If the app shows no records, load `database/seed_data.sql` into PostgreSQL or rerun `docker compose down -v` followed by `docker compose up --build`.
- If CSV upload fails, ensure the file includes all required columns and valid dates.

## Notes

The project is intentionally modular so each page can be maintained independently while reusing the same database layer and utility functions.
