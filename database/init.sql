CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    category VARCHAR(120) NOT NULL CHECK (category IN ('Internship', 'Full-time', 'Part-time', 'Graduate Program')),
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
