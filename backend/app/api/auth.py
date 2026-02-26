from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.security import create_token, hash_password, verify_password
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.auth import CreateUserRequest, LoginRequest, RegisterCompanyRequest, UserResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register')
def register_company(payload: RegisterCompanyRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.owner_email).first():
        raise HTTPException(status_code=400, detail='Email already exists')

    company = Company(name=payload.company_name)
    db.add(company)
    db.flush()
    owner = User(
        company_id=company.id,
        email=payload.owner_email,
        full_name=payload.owner_name,
        password_hash=hash_password(payload.password),
        role=UserRole.owner,
    )
    db.add(owner)
    db.commit()
    return {'message': 'Company registered', 'company_id': company.id}


@router.post('/login')
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access = create_token(str(user.id), timedelta(minutes=settings.access_token_expire_minutes), 'access', {'cid': user.company_id})
    refresh = create_token(str(user.id), timedelta(days=settings.refresh_token_expire_days), 'refresh', {'cid': user.company_id})
    response.set_cookie('access_token', access, httponly=True, secure=False, samesite='lax')
    response.set_cookie('refresh_token', refresh, httponly=True, secure=False, samesite='lax')
    return {'message': 'logged_in'}


@router.post('/users', response_model=UserResponse)
def create_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.owner, UserRole.manager)),
):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail='Email already exists')
    user = User(
        company_id=current_user.company_id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get('/me', response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
