from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd
import streamlit as st


CATEGORY_OPTIONS = [
    "Internship",
    "Full-time",
    "Part-time",
    "Graduate Program",
]

WORK_MODE_OPTIONS = ["Remote", "Hybrid", "Onsite"]
STATUS_OPTIONS = ["Open", "Applied", "Interviewing", "Closed", "Expired", "Archived"]
EXPERIENCE_LEVEL_OPTIONS = ["Intern", "Entry", "Mid", "Senior", "Graduate"]
CURRENCY_OPTIONS = ["USD", "EUR", "GBP", "INR", "CAD", "KES"]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def parse_skills(value: str | Iterable[str]) -> str:
    if isinstance(value, str):
        skills = [skill.strip() for skill in value.replace("\n", ",").split(",")]
    else:
        skills = [normalize_text(skill) for skill in value]
    cleaned = [skill for skill in skills if skill]
    return ", ".join(dict.fromkeys(cleaned))


def skills_to_list(value: str | None) -> List[str]:
    if not value:
        return []
    return [skill.strip() for skill in value.split(",") if skill.strip()]


def format_currency(amount: float | int | None, currency: str | None = None) -> str:
    if amount is None:
        return "-"
    prefix = currency or ""
    if prefix:
        return f"{prefix} {amount:,.2f}"
    return f"{amount:,.2f}"


def safe_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def validate_opportunity_payload(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    errors: List[str] = []
    cleaned: Dict[str, Any] = {}

    required_text_fields = [
        "company_name",
        "job_title",
        "category",
        "city",
        "country",
        "work_mode",
        "required_skills",
        "currency",
        "experience_level",
        "status",
        "source_link",
    ]

    for field in required_text_fields:
        cleaned[field] = normalize_text(payload.get(field))
        if not cleaned[field]:
            errors.append(f"{field.replace('_', ' ').title()} is required.")

    cleaned["salary_min"] = safe_float(payload.get("salary_min"))
    cleaned["salary_max"] = safe_float(payload.get("salary_max"))
    cleaned["application_deadline"] = payload.get("application_deadline")
    cleaned["created_at"] = payload.get("created_at") or datetime.utcnow()

    if cleaned["salary_min"] is None or cleaned["salary_max"] is None:
        errors.append("Both salary minimum and salary maximum are required.")
    elif cleaned["salary_min"] < 0 or cleaned["salary_max"] < 0:
        errors.append("Salary values must be positive.")
    elif cleaned["salary_min"] > cleaned["salary_max"]:
        errors.append("Salary minimum cannot be greater than salary maximum.")

    if cleaned["currency"] and len(cleaned["currency"].upper()) != 3:
        errors.append("Currency must be a 3-letter code such as USD.")
    else:
        cleaned["currency"] = cleaned["currency"].upper()

    if cleaned["category"] and cleaned["category"] not in CATEGORY_OPTIONS:
        errors.append("Select a valid category.")
    if cleaned["work_mode"] and cleaned["work_mode"] not in WORK_MODE_OPTIONS:
        errors.append("Select a valid work mode.")
    if cleaned["status"] and cleaned["status"] not in STATUS_OPTIONS:
        errors.append("Select a valid status.")
    if cleaned["experience_level"] and cleaned["experience_level"] not in EXPERIENCE_LEVEL_OPTIONS:
        errors.append("Select a valid experience level.")

    if isinstance(cleaned["application_deadline"], str):
        try:
            cleaned["application_deadline"] = date.fromisoformat(cleaned["application_deadline"])
        except ValueError:
            errors.append("Application deadline must be a valid date.")

    if cleaned["application_deadline"] is None:
        errors.append("Application deadline is required.")

    cleaned["required_skills"] = parse_skills(payload.get("required_skills", ""))
    if not cleaned["required_skills"]:
        errors.append("At least one required skill is needed.")

    cleaned["company_name"] = cleaned["company_name"].title()
    cleaned["job_title"] = cleaned["job_title"].title()
    cleaned["city"] = cleaned["city"].title()
    cleaned["country"] = cleaned["country"].title()
    cleaned["source_link"] = normalize_text(cleaned["source_link"])

    return cleaned, errors


def validate_csv_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    required_columns = {
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
    }

    errors: List[str] = []
    if df.empty:
        return df, ["The uploaded CSV file is empty."]

    columns = {column.strip() for column in df.columns}
    missing = required_columns - columns
    if missing:
        errors.append("Missing required columns: " + ", ".join(sorted(missing)))
        return df, errors

    normalized = df.copy()
    normalized.columns = [column.strip() for column in normalized.columns]
    normalized["company_name"] = normalized["company_name"].map(normalize_text).str.title()
    normalized["job_title"] = normalized["job_title"].map(normalize_text).str.title()
    normalized["category"] = normalized["category"].map(normalize_text)
    normalized["city"] = normalized["city"].map(normalize_text).str.title()
    normalized["country"] = normalized["country"].map(normalize_text).str.title()
    normalized["work_mode"] = normalized["work_mode"].map(normalize_text).str.title()
    normalized["required_skills"] = normalized["required_skills"].map(parse_skills)
    normalized["currency"] = normalized["currency"].map(normalize_text).str.upper()
    normalized["experience_level"] = normalized["experience_level"].map(normalize_text)
    normalized["status"] = normalized["status"].map(normalize_text).str.title()
    normalized["source_link"] = normalized["source_link"].map(normalize_text)

    normalized["salary_min"] = pd.to_numeric(normalized["salary_min"], errors="coerce")
    normalized["salary_max"] = pd.to_numeric(normalized["salary_max"], errors="coerce")
    normalized["application_deadline"] = pd.to_datetime(normalized["application_deadline"], errors="coerce").dt.date

    for idx, row in normalized.iterrows():
        row_errors: List[str] = []
        for field in ["company_name", "job_title", "category", "city", "country", "work_mode", "required_skills", "currency", "experience_level", "status", "source_link"]:
            if not row[field]:
                row_errors.append(f"Row {idx + 1}: {field.replace('_', ' ').title()} is required.")
        if pd.isna(row["salary_min"]) or pd.isna(row["salary_max"]):
            row_errors.append(f"Row {idx + 1}: salary_min and salary_max must be numeric.")
        elif float(row["salary_min"]) > float(row["salary_max"]):
            row_errors.append(f"Row {idx + 1}: salary_min cannot exceed salary_max.")
        if pd.isna(row["application_deadline"]):
            row_errors.append(f"Row {idx + 1}: application_deadline must be a valid date.")
        if len(str(row["currency"])) != 3:
            row_errors.append(f"Row {idx + 1}: currency must be a 3-letter code.")
        if row["category"] not in CATEGORY_OPTIONS:
            row_errors.append(f"Row {idx + 1}: invalid category.")
        if row["work_mode"] not in WORK_MODE_OPTIONS:
            row_errors.append(f"Row {idx + 1}: invalid work mode.")
        if row["status"] not in STATUS_OPTIONS:
            row_errors.append(f"Row {idx + 1}: invalid status.")
        if row["experience_level"] not in EXPERIENCE_LEVEL_OPTIONS:
            row_errors.append(f"Row {idx + 1}: invalid experience level.")
        errors.extend(row_errors)

    normalized = normalized.dropna(subset=["salary_min", "salary_max", "application_deadline"])
    normalized["created_at"] = datetime.utcnow()
    return normalized, errors


def paginate_dataframe(df: pd.DataFrame, page: int, page_size: int) -> pd.DataFrame:
    if df.empty:
        return df
    start = max(page - 1, 0) * page_size
    end = start + page_size
    return df.iloc[start:end].copy()


def unique_preserve_order(values: Iterable[str]) -> List[str]:
    return list(dict.fromkeys(value for value in values if value))


def top_skills_frame(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    if df.empty or "required_skills" not in df.columns:
        return pd.DataFrame(columns=["skill", "count"])
    skills: List[str] = []
    for value in df["required_skills"].dropna().astype(str):
        skills.extend(skills_to_list(value))
    if not skills:
        return pd.DataFrame(columns=["skill", "count"])
    counts = pd.Series(skills).value_counts().head(limit).reset_index()
    counts.columns = ["skill", "count"]
    return counts


def deadline_bucket_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "application_deadline" not in df.columns:
        return pd.DataFrame(columns=["deadline", "count"])
    frame = df.copy()
    frame["application_deadline"] = pd.to_datetime(frame["application_deadline"], errors="coerce")
    frame = frame.dropna(subset=["application_deadline"])
    frame["deadline"] = frame["application_deadline"].dt.date
    return frame.groupby("deadline").size().reset_index(name="count").sort_values("deadline")


def render_section_title(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
