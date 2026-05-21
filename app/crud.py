from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models import TRMEntry


def get_trm_entries(
    db: Session,
    skip: int = 0,
    limit: int = 2000,
    application: Optional[str] = None,
    has_vulnerabilities: Optional[bool] = None,
    active: Optional[bool] = None,
    search: Optional[str] = None,
) -> List[TRMEntry]:
    query = db.query(TRMEntry)
    if application:
        query = query.filter(TRMEntry.application == application)
    if has_vulnerabilities is not None:
        query = query.filter(TRMEntry.has_vulnerabilities == has_vulnerabilities)
    if active is not None:
        query = query.filter(TRMEntry.active == active)
    if search:
        query = query.filter(
            or_(
                TRMEntry.tool_name.ilike(f"%{search}%"),
                TRMEntry.application.ilike(f"%{search}%"),
                TRMEntry.managed_by.ilike(f"%{search}%"),
                TRMEntry.notes.ilike(f"%{search}%"),
            )
        )
    return query.order_by(TRMEntry.application, TRMEntry.tool_name).offset(skip).limit(limit).all()


def get_trm_entry(db: Session, entry_id: int) -> Optional[TRMEntry]:
    return db.query(TRMEntry).filter(TRMEntry.id == entry_id).first()


def create_trm_entry(db: Session, **kwargs) -> TRMEntry:
    db_entry = TRMEntry(**kwargs)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def update_trm_entry(db: Session, entry_id: int, **kwargs) -> Optional[TRMEntry]:
    db_entry = db.query(TRMEntry).filter(TRMEntry.id == entry_id).first()
    if not db_entry:
        return None
    for key, value in kwargs.items():
        setattr(db_entry, key, value)
    db_entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_trm_entry(db: Session, entry_id: int) -> bool:
    db_entry = db.query(TRMEntry).filter(TRMEntry.id == entry_id).first()
    if not db_entry:
        return False
    db.delete(db_entry)
    db.commit()
    return True


def get_applications(db: Session) -> List[str]:
    results = db.query(TRMEntry.application).distinct().order_by(TRMEntry.application).all()
    return [r[0] for r in results]


def get_stats(db: Session) -> dict:
    today = date.today()

    total = db.query(TRMEntry).count()
    active_count = db.query(TRMEntry).filter(TRMEntry.active == True).count()
    with_vulns = db.query(TRMEntry).filter(TRMEntry.has_vulnerabilities == True).count()
    open_source_count = db.query(TRMEntry).filter(TRMEntry.open_source == True).count()
    aor_submitted_count = db.query(TRMEntry).filter(TRMEntry.aor_submitted == True).count()

    eol_passed = db.query(TRMEntry).filter(
        TRMEntry.product_eol.isnot(None), TRMEntry.product_eol < today
    ).count()
    eol_within_3mo = db.query(TRMEntry).filter(
        TRMEntry.product_eol.isnot(None),
        TRMEntry.product_eol >= today,
        TRMEntry.product_eol <= today + timedelta(days=90),
    ).count()
    eol_within_6mo = db.query(TRMEntry).filter(
        TRMEntry.product_eol.isnot(None),
        TRMEntry.product_eol > today + timedelta(days=90),
        TRMEntry.product_eol <= today + timedelta(days=180),
    ).count()
    eol_within_1yr = db.query(TRMEntry).filter(
        TRMEntry.product_eol.isnot(None),
        TRMEntry.product_eol > today + timedelta(days=180),
        TRMEntry.product_eol <= today + timedelta(days=365),
    ).count()
    eol_over_1yr = db.query(TRMEntry).filter(
        TRMEntry.product_eol.isnot(None),
        TRMEntry.product_eol > today + timedelta(days=365),
    ).count()
    no_eol = db.query(TRMEntry).filter(TRMEntry.product_eol.is_(None)).count()

    by_app = (
        db.query(TRMEntry.application, func.count(TRMEntry.id))
        .group_by(TRMEntry.application)
        .order_by(func.count(TRMEntry.id).desc())
        .all()
    )

    upcoming_eols = (
        db.query(TRMEntry)
        .filter(
            TRMEntry.product_eol.isnot(None),
            TRMEntry.product_eol >= today,
            TRMEntry.product_eol <= today + timedelta(days=365),
        )
        .order_by(TRMEntry.product_eol)
        .all()
    )

    past_eols = (
        db.query(TRMEntry)
        .filter(TRMEntry.product_eol.isnot(None), TRMEntry.product_eol < today)
        .order_by(TRMEntry.product_eol.desc())
        .all()
    )

    return {
        "total": total,
        "active": active_count,
        "inactive": total - active_count,
        "with_vulnerabilities": with_vulns,
        "without_vulnerabilities": total - with_vulns,
        "open_source": open_source_count,
        "commercial": total - open_source_count,
        "eol_passed": eol_passed,
        "eol_within_3_months": eol_within_3mo,
        "eol_within_6_months": eol_within_6mo,
        "eol_within_1_year": eol_within_1yr,
        "eol_over_1_year": eol_over_1yr,
        "no_eol_set": no_eol,
        "by_application": [{"application": app, "count": cnt} for app, cnt in by_app],
        "aor_submitted": aor_submitted_count,
        "aor_not_submitted": total - aor_submitted_count,
        "upcoming_eols": [
            {
                "id": e.id,
                "tool_name": e.tool_name,
                "application": e.application,
                "eol_date": e.product_eol.isoformat(),
                "days_until_eol": (e.product_eol - today).days,
                "current_version": e.current_version,
            }
            for e in upcoming_eols
        ],
        "past_eols": [
            {
                "id": e.id,
                "tool_name": e.tool_name,
                "application": e.application,
                "eol_date": e.product_eol.isoformat(),
                "days_past_eol": (today - e.product_eol).days,
                "current_version": e.current_version,
                "active": e.active,
            }
            for e in past_eols
        ],
    }
