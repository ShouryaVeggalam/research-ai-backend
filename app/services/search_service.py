"""Global search across all intelligence entities."""
from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.intelligence import (
    Competitor,
    Industry,
    Market,
    Opportunity,
    Risk,
    Trend,
)
from app.models.reports import ResearchReport
from app.schemas.dashboard import SearchHit, SearchResponse

# (model, entity_type, title_field, secondary_field)
_SEARCHABLE = [
    (Market, "market", "name", "description"),
    (Competitor, "competitor", "name", "description"),
    (Industry, "industry", "name", "description"),
    (Opportunity, "opportunity", "title", "description"),
    (Risk, "risk", "title", "description"),
    (Trend, "trend", "name", "description"),
    (ResearchReport, "report", "title", "summary"),
]


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search(self, company_id: str, query: str, *, limit_per_type: int = 5) -> SearchResponse:
        q = (query or "").strip()
        hits: list[SearchHit] = []
        if not q:
            return SearchResponse(query=query, total=0, hits=[])

        pattern = f"%{q.lower()}%"
        for model, entity_type, title_field, secondary in _SEARCHABLE:
            title_col = getattr(model, title_field)
            sec_col = getattr(model, secondary)
            stmt = (
                select(model)
                .where(
                    model.company_id == company_id,
                    or_(title_col.ilike(pattern), sec_col.ilike(pattern)),
                )
                .limit(limit_per_type)
            )
            for obj in self.db.execute(stmt).scalars().all():
                title = getattr(obj, title_field)
                snippet = getattr(obj, secondary)
                score = 1.0 if q.lower() in (title or "").lower() else 0.6
                hits.append(
                    SearchHit(
                        entity_type=entity_type,
                        id=obj.id,
                        title=title,
                        snippet=(snippet[:160] if snippet else None),
                        score=score,
                    )
                )

        hits.sort(key=lambda h: h.score, reverse=True)
        return SearchResponse(query=query, total=len(hits), hits=hits)
