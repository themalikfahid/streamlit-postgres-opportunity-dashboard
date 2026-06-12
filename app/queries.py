from __future__ import annotations

from typing import Dict, Tuple

OPPORTUNITY_COLUMNS = [
    "opportunity_id",
    "company_name",
    "job_title",
    "category",
    "city",
    "country",
    "work_mode",
    "required_skills",
    "salary_min",
    "salary_max",
    "currency",
    "experience_level",
    "application_deadline",
    "status",
    "source_link",
    "created_at",
]

OPPORTUNITY_INSERT_COLUMNS = [
    "company_name",
    "job_title",
    "category",
    "city",
    "country",
    "work_mode",
    "required_skills",
    "salary_min",
    "salary_max",
    "currency",
    "experience_level",
    "application_deadline",
    "status",
    "source_link",
    "created_at",
]

FILTER_COLUMNS = {
    "category": "category",
    "work_mode": "work_mode",
    "status": "status",
    "city": "city",
    "country": "country",
    "company_name": "company_name",
    "experience_level": "experience_level",
}

ALLOWED_SORT_COLUMNS = {
    "created_at",
    "application_deadline",
    "salary_min",
    "salary_max",
    "company_name",
    "job_title",
    "status",
    "city",
}


def build_select_query(
    filters: Dict[str, str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "DESC",
) -> Tuple[str, Dict[str, object]]:
    filters = filters or {}
    clauses = ["SELECT * FROM opportunities"]
    where: list[str] = []
    params: Dict[str, object] = {}

    search_value = filters.get("search")
    if search_value:
        where.append(
            "(" 
            "company_name ILIKE :search OR job_title ILIKE :search OR category ILIKE :search OR "
            "city ILIKE :search OR country ILIKE :search OR work_mode ILIKE :search OR "
            "required_skills ILIKE :search OR status ILIKE :search OR source_link ILIKE :search"
            ")"
        )
        params["search"] = f"%{search_value}%"

    for key, column in FILTER_COLUMNS.items():
        value = filters.get(key)
        if value:
            where.append(f"{column} = :{key}")
            params[key] = value

    if filters.get("deadline_from"):
        where.append("application_deadline >= :deadline_from")
        params["deadline_from"] = filters["deadline_from"]
    if filters.get("deadline_to"):
        where.append("application_deadline <= :deadline_to")
        params["deadline_to"] = filters["deadline_to"]

    if where:
        clauses.append("WHERE " + " AND ".join(where))

    sort_column = sort_by if sort_by in ALLOWED_SORT_COLUMNS else "created_at"
    sort_direction = "ASC" if str(sort_order).upper() == "ASC" else "DESC"
    clauses.append(f"ORDER BY {sort_column} {sort_direction}")

    if limit is not None:
        clauses.append("LIMIT :limit")
        params["limit"] = int(limit)
    if offset is not None:
        clauses.append("OFFSET :offset")
        params["offset"] = int(offset)

    return "\n".join(clauses), params


def build_count_query(filters: Dict[str, str] | None = None) -> Tuple[str, Dict[str, object]]:
    query, params = build_select_query(filters=filters, limit=None, offset=None)
    count_query = query.replace("SELECT *", "SELECT COUNT(*) AS row_count", 1).split("ORDER BY")[0].strip()
    return count_query, params


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    category VARCHAR(120) NOT NULL,
    city VARCHAR(120) NOT NULL,
    country VARCHAR(120) NOT NULL,
    work_mode VARCHAR(20) NOT NULL CHECK (work_mode IN ('Remote', 'Hybrid', 'Onsite')),
    required_skills TEXT NOT NULL,
    salary_min NUMERIC(12, 2) NOT NULL CHECK (salary_min >= 0),
    salary_max NUMERIC(12, 2) NOT NULL CHECK (salary_max >= 0),
    currency CHAR(3) NOT NULL,
    experience_level VARCHAR(40) NOT NULL,
    application_deadline DATE NOT NULL,
    status VARCHAR(30) NOT NULL CHECK (status IN ('Open', 'Applied', 'Interviewing', 'Closed', 'Expired', 'Archived')),
    source_link TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT salary_range_check CHECK (salary_min <= salary_max)
);

CREATE INDEX IF NOT EXISTS idx_opportunities_category ON opportunities (category);
CREATE INDEX IF NOT EXISTS idx_opportunities_city ON opportunities (city);
CREATE INDEX IF NOT EXISTS idx_opportunities_country ON opportunities (country);
CREATE INDEX IF NOT EXISTS idx_opportunities_work_mode ON opportunities (work_mode);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities (status);
CREATE INDEX IF NOT EXISTS idx_opportunities_deadline ON opportunities (application_deadline);
CREATE INDEX IF NOT EXISTS idx_opportunities_company_job ON opportunities (company_name, job_title);
"""
