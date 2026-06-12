from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv
import os

from queries import OPPORTUNITY_COLUMNS, OPPORTUNITY_INSERT_COLUMNS, build_count_query, build_select_query
from utils import normalize_text, parse_skills

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_DIR = BASE_DIR / "database"
INIT_SQL_FILE = DATABASE_DIR / "init.sql"

DB_HOST = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "postgres_db"))
DB_PORT = int(os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432")))
DB_NAME = os.getenv("POSTGRES_DB", "student_opportunities_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")


def get_database_url() -> str:
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    engine = create_engine(get_database_url(), pool_pre_ping=True, future=True)
    _ensure_schema(engine)
    return engine


@contextmanager
def get_raw_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _ensure_schema(engine: Engine) -> None:
    if not INIT_SQL_FILE.exists():
        return
    with engine.begin() as connection:
        connection.execute(text(INIT_SQL_FILE.read_text(encoding="utf-8")))


def _normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = dict(record)
    cleaned["company_name"] = normalize_text(cleaned.get("company_name", "")).title()
    cleaned["job_title"] = normalize_text(cleaned.get("job_title", "")).title()
    cleaned["category"] = normalize_text(cleaned.get("category", ""))
    cleaned["city"] = normalize_text(cleaned.get("city", "")).title()
    cleaned["country"] = normalize_text(cleaned.get("country", "")).title()
    cleaned["work_mode"] = normalize_text(cleaned.get("work_mode", "")).title()
    cleaned["required_skills"] = parse_skills(cleaned.get("required_skills", ""))
    cleaned["currency"] = normalize_text(cleaned.get("currency", "USD")).upper()
    cleaned["experience_level"] = normalize_text(cleaned.get("experience_level", ""))
    cleaned["status"] = normalize_text(cleaned.get("status", "")).title()
    cleaned["source_link"] = normalize_text(cleaned.get("source_link", ""))
    if isinstance(cleaned.get("application_deadline"), str):
        cleaned["application_deadline"] = date.fromisoformat(cleaned["application_deadline"])
    if isinstance(cleaned.get("created_at"), str):
        cleaned["created_at"] = datetime.fromisoformat(cleaned["created_at"])
    return cleaned


def _record_to_row(record: Dict[str, Any]) -> Dict[str, Any]:
    return {column: record.get(column) for column in OPPORTUNITY_INSERT_COLUMNS}


def create_opportunity(record: Dict[str, Any]) -> int:
    cleaned = _normalize_record(record)
    query = f"""
        INSERT INTO opportunities ({', '.join(OPPORTUNITY_INSERT_COLUMNS)})
        VALUES ({', '.join(f':{column}' for column in OPPORTUNITY_INSERT_COLUMNS)})
        RETURNING opportunity_id
    """
    with get_engine().begin() as connection:
        result = connection.execute(text(query), _record_to_row(cleaned))
        inserted_id = result.scalar_one()
    return int(inserted_id)


def get_opportunities(
    filters: Dict[str, Any] | None = None,
    limit: int | None = None,
    offset: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "DESC",
) -> pd.DataFrame:
    query, params = build_select_query(filters=filters, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
    with get_engine().begin() as connection:
        frame = pd.read_sql_query(text(query), connection, params=params)
    return frame


def count_opportunities(filters: Dict[str, Any] | None = None) -> int:
    query, params = build_count_query(filters=filters)
    with get_engine().begin() as connection:
        result = connection.execute(text(query), params)
        value = result.scalar_one()
    return int(value)


def get_opportunity_by_id(opportunity_id: int) -> pd.Series | None:
    frame = get_opportunities(filters={"search": ""}, limit=None)
    if frame.empty:
        return None
    matched = frame.loc[frame["opportunity_id"] == opportunity_id]
    if matched.empty:
        return None
    return matched.iloc[0]


def update_opportunity(opportunity_id: int, updates: Dict[str, Any]) -> bool:
    if not updates:
        return False
    assignments = ", ".join(f"{column} = :{column}" for column in updates.keys())
    query = f"UPDATE opportunities SET {assignments} WHERE opportunity_id = :opportunity_id"
    params = dict(updates)
    params["opportunity_id"] = opportunity_id
    with get_engine().begin() as connection:
        result = connection.execute(text(query), params)
    return result.rowcount > 0


def delete_opportunity(opportunity_id: int) -> bool:
    with get_engine().begin() as connection:
        result = connection.execute(text("DELETE FROM opportunities WHERE opportunity_id = :opportunity_id"), {"opportunity_id": opportunity_id})
    return result.rowcount > 0


def bulk_insert(records: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    normalized_records: List[Dict[str, Any]] = [_normalize_record(record) for record in records]
    if not normalized_records:
        return {"inserted": 0, "skipped": 0, "total": 0}

    values = [tuple(record.get(column) for column in OPPORTUNITY_INSERT_COLUMNS) for record in normalized_records]
    template = "(" + ", ".join(["%s"] * len(OPPORTUNITY_INSERT_COLUMNS)) + ")"
    query = f"""
        INSERT INTO opportunities ({', '.join(OPPORTUNITY_INSERT_COLUMNS)})
        VALUES %s
        ON CONFLICT (source_link) DO NOTHING
        RETURNING opportunity_id
    """

    with get_raw_connection() as connection:
        with connection.cursor() as cursor:
            inserted_rows = execute_values(cursor, query, values, template=template, fetch=True)
    inserted = len(inserted_rows or [])
    total = len(normalized_records)
    return {"inserted": inserted, "skipped": total - inserted, "total": total}


def duplicate_check() -> pd.DataFrame:
    query = """
        SELECT
            company_name,
            job_title,
            city,
            source_link,
            COUNT(*) AS duplicate_count,
            MIN(opportunity_id) AS first_occurrence_id,
            MAX(created_at) AS latest_created_at
        FROM opportunities
        GROUP BY company_name, job_title, city, source_link
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC, company_name, job_title
    """
    with get_engine().begin() as connection:
        frame = pd.read_sql_query(text(query), connection)
    return frame


def get_deadline_alerts(days: int = 7) -> pd.DataFrame:
    query = """
        SELECT *
        FROM opportunities
        WHERE application_deadline BETWEEN CURRENT_DATE AND CURRENT_DATE + :days
        ORDER BY application_deadline ASC
    """
    with get_engine().begin() as connection:
        frame = pd.read_sql_query(text(query), connection, params={"days": days})
    return frame


def get_expired_jobs() -> pd.DataFrame:
    query = """
        SELECT *
        FROM opportunities
        WHERE application_deadline < CURRENT_DATE
        ORDER BY application_deadline DESC
    """
    with get_engine().begin() as connection:
        frame = pd.read_sql_query(text(query), connection)
    return frame


def get_table_structure() -> pd.DataFrame:
    query = """
        SELECT
            ordinal_position,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'opportunities'
        ORDER BY ordinal_position
    """
    with get_engine().begin() as connection:
        frame = pd.read_sql_query(text(query), connection)
    return frame


def get_postgres_version() -> str:
    with get_engine().begin() as connection:
        value = connection.execute(text("SELECT version()"))
        version = value.scalar_one()
    return str(version)
