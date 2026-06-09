"""Background jobs run by Celery workers / beat.

Each scheduled job iterates over all active companies and runs the relevant
intelligence refresh. Jobs are idempotent and use their own DB sessions.
"""
from __future__ import annotations

from app.core.constants import ReportType
from app.core.logging import get_logger
from app.database.session import session_scope
from app.repositories.user import CompanyRepository
from app.services.opportunity_engine import OpportunityEngine
from app.services.orchestration_service import OrchestrationService
from app.services.report_service import ReportService
from app.services.risk_engine import RiskEngine
from app.workers.celery_app import celery_app

logger = get_logger("workers.jobs")


def _active_company_ids() -> list[str]:
    with session_scope() as db:
        companies = CompanyRepository(db).list(limit=1000, is_active=True)
        return [c.id for c in companies]


@celery_app.task(name="jobs.signal_refresh")
def signal_refresh() -> dict:
    """Re-run the market/customer agents to reprocess recent signals."""
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            OrchestrationService(db).run_agent(company_id, "market")
            OrchestrationService(db).run_agent(company_id, "customer")
        count += 1
    logger.info("job.signal_refresh", companies=count)
    return {"companies": count}


@celery_app.task(name="jobs.trend_refresh")
def trend_refresh() -> dict:
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            OrchestrationService(db).run_agent(company_id, "trend")
        count += 1
    logger.info("job.trend_refresh", companies=count)
    return {"companies": count}


@celery_app.task(name="jobs.competitor_refresh")
def competitor_refresh() -> dict:
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            OrchestrationService(db).run_agent(company_id, "competitor")
        count += 1
    logger.info("job.competitor_refresh", companies=count)
    return {"companies": count}


@celery_app.task(name="jobs.opportunity_refresh")
def opportunity_refresh() -> dict:
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            OpportunityEngine(db).generate(company_id, persist=True)
        count += 1
    logger.info("job.opportunity_refresh", companies=count)
    return {"companies": count}


@celery_app.task(name="jobs.risk_refresh")
def risk_refresh() -> dict:
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            RiskEngine(db).compute(company_id, persist=True)
        count += 1
    logger.info("job.risk_refresh", companies=count)
    return {"companies": count}


@celery_app.task(name="jobs.daily_executive_brief")
def daily_executive_brief() -> dict:
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            ReportService(db).generate_brief(company_id, ReportType.DAILY)
        count += 1
    logger.info("job.daily_executive_brief", companies=count)
    return {"companies": count}


@celery_app.task(name="jobs.weekly_research_report")
def weekly_research_report() -> dict:
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            ReportService(db).generate_research_report(company_id, ReportType.WEEKLY)
        count += 1
    logger.info("job.weekly_research_report", companies=count)
    return {"companies": count}


@celery_app.task(name="jobs.monthly_strategic_outlook")
def monthly_strategic_outlook() -> dict:
    count = 0
    for company_id in _active_company_ids():
        with session_scope() as db:
            ReportService(db).generate_research_report(company_id, ReportType.MONTHLY)
        count += 1
    logger.info("job.monthly_strategic_outlook", companies=count)
    return {"companies": count}
