from pydantic import BaseModel, EmailStr


class RegisterCompanyRequest(BaseModel):
    company_name: str
    owner_email: EmailStr
    owner_password: str
    owner_full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class RefreshRequest(BaseModel):
    refresh_token: str | None = None
