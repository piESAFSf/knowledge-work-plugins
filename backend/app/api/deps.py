from fastapi import Depends, Header, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import ApiKey, User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get('type') != 'access':
            raise HTTPException(status_code=401, detail='Invalid token type')
    except JWTError as exc:
        raise HTTPException(status_code=401, detail='Invalid token') from exc

    user = db.query(User).filter(User.id == payload['sub']).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user


def require_roles(*roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail='Forbidden')
        return user

    return checker


def require_api_key(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    key = db.query(ApiKey).filter(ApiKey.key == x_api_key, ApiKey.is_active.is_(True)).first()
    if not key:
        raise HTTPException(status_code=401, detail='Invalid API key')
    return key.company_id
