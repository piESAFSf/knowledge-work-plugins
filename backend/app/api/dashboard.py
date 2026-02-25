from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Company, Conversation
from app.schemas.dashboard import UsageStats

router = APIRouter(prefix='/dashboard', tags=['dashboard'])


@router.get('/usage', response_model=UsageStats)
def usage_stats(db: Session = Depends(get_db), current=Depends(get_current_user)):
    company = db.query(Company).filter(Company.id == current.company_id).one()
    count = db.query(Conversation).filter(Conversation.company_id == current.company_id).count()
    return UsageStats(
        plan=company.subscription_plan,
        monthly_quota=company.monthly_quota,
        used_quota=company.used_quota,
        remaining_quota=max(0, company.monthly_quota - company.used_quota),
        conversation_count=count,
    )
