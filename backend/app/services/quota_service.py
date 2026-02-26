from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.usage import UsageRecord


def get_company_usage(db: Session, company_id: int) -> int:
    total = db.query(func.coalesce(func.sum(UsageRecord.amount), 0)).filter(UsageRecord.company_id == company_id).scalar()
    return int(total or 0)


def ensure_quota(db: Session, company: Company, increment: int = 1) -> bool:
    return get_company_usage(db, company.id) + increment <= company.quota_limit
