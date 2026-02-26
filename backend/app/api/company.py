from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.company import Company
from app.models.conversation import Conversation
from app.models.subscription import Subscription
from app.models.usage import UsageRecord
from app.models.user import User, UserRole
from app.schemas.company import CompanyResponse

router = APIRouter(prefix='/company', tags=['company'])


@router.get('/current', response_model=CompanyResponse)
def current_company(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Company).filter(Company.id == user.company_id).first()


@router.get('/dashboard')
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    company_id = user.company_id
    usage = db.query(func.coalesce(func.sum(UsageRecord.amount), 0)).filter(UsageRecord.company_id == company_id).scalar() or 0
    members = db.query(func.count(User.id)).filter(User.company_id == company_id).scalar() or 0
    conversations = db.query(func.count(Conversation.id)).filter(Conversation.company_id == company_id).scalar() or 0
    subscription = db.query(Subscription).filter(Subscription.company_id == company_id).order_by(Subscription.id.desc()).first()

    return {
        'usage': int(usage),
        'members': int(members),
        'conversations': int(conversations),
        'plan': subscription.plan if subscription else 'free',
        'subscription_status': subscription.status if subscription else 'inactive',
    }


@router.get('/users')
def list_users(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.owner, UserRole.manager))):
    return db.query(User).filter(User.company_id == user.company_id).all()
