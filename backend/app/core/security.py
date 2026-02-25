from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_token(subject: str, token_type: str, expires_delta: timedelta, extra: dict[str, Any] | None = None) -> str:
    payload: dict[str, Any] = {
        'sub': subject,
        'type': token_type,
        'exp': datetime.now(timezone.utc) + expires_delta,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, company_id: str, role: str) -> str:
    return create_token(
        subject=user_id,
        token_type='access',
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra={'company_id': company_id, 'role': role},
    )


def create_refresh_token(user_id: str) -> str:
    return create_token(
        subject=user_id,
        token_type='refresh',
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )
