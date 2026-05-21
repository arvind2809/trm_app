from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text

from app.database import Base


class TRMEntry(Base):
    __tablename__ = "trm_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    application = Column(String(200), nullable=False, index=True)
    tool_name = Column(String(200), nullable=False)
    current_version = Column(String(100), nullable=True)
    latest_version = Column(String(100), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    open_source = Column(Boolean, default=True, nullable=False)
    product_eol = Column(Date, nullable=True)
    eol_url = Column(String(500), nullable=True)
    gsa_gear_url = Column(String(500), nullable=True)
    download_url = Column(String(500), nullable=True)
    has_vulnerabilities = Column(Boolean, default=False, nullable=False)
    cve_report_link = Column(String(500), nullable=True)
    aor_submitted = Column(Boolean, default=False, nullable=False)
    aor_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    managed_by = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(200), nullable=True, default="system")
    updated_by = Column(String(200), nullable=True, default="system")
