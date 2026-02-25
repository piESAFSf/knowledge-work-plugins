from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.security import hash_password
from app.models import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix='/users', tags=['users'])


@router.post('', response_model=UserOut, dependencies=[Depends(require_roles('owner', 'manager'))])
def create_user(payload: UserCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        company_id=current.company_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get('', response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current=Depends(get_current_user)):
    return db.query(User).filter(User.company_id == current.company_id).all()
