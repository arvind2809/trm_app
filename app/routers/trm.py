from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import app.crud as crud
from app.database import get_db

router = APIRouter(prefix="/trm", tags=["trm"])
templates = Jinja2Templates(directory="templates")


def _parse_bool(value: Optional[str]) -> bool:
    return value == "on"


def _parse_date(value: Optional[str]) -> Optional[date]:
    if value and value.strip():
        return date.fromisoformat(value.strip())
    return None


def _clean(value: Optional[str]) -> Optional[str]:
    if value and value.strip():
        return value.strip()
    return None


@router.get("/visualization", response_class=HTMLResponse)
async def visualization(request: Request):
    return templates.TemplateResponse(request, "trm/visualization.html")


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


@router.get("/{entry_id}/json")
async def get_entry_json(entry_id: int, db: Session = Depends(get_db)):
    entry = crud.get_trm_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {
        "id": entry.id,
        "application": entry.application or "",
        "tool_name": entry.tool_name or "",
        "current_version": entry.current_version or "",
        "latest_version": entry.latest_version or "",
        "active": entry.active,
        "open_source": entry.open_source,
        "product_eol": entry.product_eol.isoformat() if entry.product_eol else "",
        "eol_url": entry.eol_url or "",
        "gsa_gear_url": entry.gsa_gear_url or "",
        "download_url": entry.download_url or "",
        "has_vulnerabilities": entry.has_vulnerabilities,
        "cve_report_link": entry.cve_report_link or "",
        "aor_submitted": entry.aor_submitted,
        "aor_date": entry.aor_date.isoformat() if entry.aor_date else "",
        "notes": entry.notes or "",
        "managed_by": entry.managed_by or "",
        "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M"),
        "updated_at": entry.updated_at.strftime("%Y-%m-%d %H:%M"),
        "created_by": entry.created_by or "",
        "updated_by": entry.updated_by or "",
    }


@router.get("/new", response_class=HTMLResponse)
async def new_entry_form(request: Request, db: Session = Depends(get_db)):
    applications = crud.get_applications(db)
    return templates.TemplateResponse(
        request,
        "trm/form.html",
        {
            "entry": None,
            "applications": applications,
            "action": "/trm/new",
            "title": "Add TRM Entry",
        },
    )


@router.post("/new")
async def create_entry(
    request: Request,
    db: Session = Depends(get_db),
    application: str = Form(...),
    tool_name: str = Form(...),
    current_version: Optional[str] = Form(None),
    latest_version: Optional[str] = Form(None),
    active: Optional[str] = Form(None),
    open_source: Optional[str] = Form(None),
    product_eol: Optional[str] = Form(None),
    eol_url: Optional[str] = Form(None),
    gsa_gear_url: Optional[str] = Form(None),
    download_url: Optional[str] = Form(None),
    has_vulnerabilities: Optional[str] = Form(None),
    cve_report_link: Optional[str] = Form(None),
    aor_submitted: Optional[str] = Form(None),
    aor_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    managed_by: Optional[str] = Form(None),
):
    crud.create_trm_entry(
        db,
        application=application.strip(),
        tool_name=tool_name.strip(),
        current_version=_clean(current_version),
        latest_version=_clean(latest_version),
        active=_parse_bool(active),
        open_source=_parse_bool(open_source),
        product_eol=_parse_date(product_eol),
        eol_url=_clean(eol_url),
        gsa_gear_url=_clean(gsa_gear_url),
        download_url=_clean(download_url),
        has_vulnerabilities=_parse_bool(has_vulnerabilities),
        cve_report_link=_clean(cve_report_link),
        aor_submitted=_parse_bool(aor_submitted),
        aor_date=_parse_date(aor_date),
        notes=_clean(notes),
        managed_by=_clean(managed_by),
        created_by="admin",
        updated_by="admin",
    )
    return RedirectResponse(url="/trm?msg=created", status_code=303)


@router.get("/{entry_id}/edit", response_class=HTMLResponse)
async def edit_entry_form(
    request: Request, entry_id: int, db: Session = Depends(get_db)
):
    entry = crud.get_trm_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    applications = crud.get_applications(db)
    return templates.TemplateResponse(
        request,
        "trm/form.html",
        {
            "entry": entry,
            "applications": applications,
            "action": f"/trm/{entry_id}/edit",
            "title": f"Edit: {entry.tool_name}",
        },
    )


@router.post("/{entry_id}/edit")
async def update_entry(
    request: Request,
    entry_id: int,
    db: Session = Depends(get_db),
    application: str = Form(...),
    tool_name: str = Form(...),
    current_version: Optional[str] = Form(None),
    latest_version: Optional[str] = Form(None),
    active: Optional[str] = Form(None),
    open_source: Optional[str] = Form(None),
    product_eol: Optional[str] = Form(None),
    eol_url: Optional[str] = Form(None),
    gsa_gear_url: Optional[str] = Form(None),
    download_url: Optional[str] = Form(None),
    has_vulnerabilities: Optional[str] = Form(None),
    cve_report_link: Optional[str] = Form(None),
    aor_submitted: Optional[str] = Form(None),
    aor_date: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    managed_by: Optional[str] = Form(None),
):
    result = crud.update_trm_entry(
        db,
        entry_id,
        application=application.strip(),
        tool_name=tool_name.strip(),
        current_version=_clean(current_version),
        latest_version=_clean(latest_version),
        active=_parse_bool(active),
        open_source=_parse_bool(open_source),
        product_eol=_parse_date(product_eol),
        eol_url=_clean(eol_url),
        gsa_gear_url=_clean(gsa_gear_url),
        download_url=_clean(download_url),
        has_vulnerabilities=_parse_bool(has_vulnerabilities),
        cve_report_link=_clean(cve_report_link),
        aor_submitted=_parse_bool(aor_submitted),
        aor_date=_parse_date(aor_date),
        notes=_clean(notes),
        managed_by=_clean(managed_by),
        updated_by="admin",
    )
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return RedirectResponse(url="/trm?msg=updated", status_code=303)


@router.post("/{entry_id}/delete")
async def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    result = crud.delete_trm_entry(db, entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return RedirectResponse(url="/trm?msg=deleted", status_code=303)


@router.get("/", response_class=HTMLResponse)
async def list_entries(
    request: Request,
    db: Session = Depends(get_db),
    application: Optional[str] = None,
    has_vulnerabilities: Optional[str] = None,
    active: Optional[str] = None,
    search: Optional[str] = None,
    msg: Optional[str] = None,
):
    vuln_filter = None
    if has_vulnerabilities == "true":
        vuln_filter = True
    elif has_vulnerabilities == "false":
        vuln_filter = False

    active_filter = None
    if active == "true":
        active_filter = True
    elif active == "false":
        active_filter = False

    entries = crud.get_trm_entries(
        db,
        application=application if application else None,
        has_vulnerabilities=vuln_filter,
        active=active_filter,
        search=search if search else None,
    )
    applications = crud.get_applications(db)
    today = date.today()

    return templates.TemplateResponse(
        request,
        "trm/list.html",
        {
            "entries": entries,
            "applications": applications,
            "current_application": application or "",
            "current_has_vulnerabilities": has_vulnerabilities or "",
            "current_active": active or "",
            "current_search": search or "",
            "msg": msg,
            "today": today,
        },
    )
