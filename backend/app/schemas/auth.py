from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class RegisterCompanyRequest(BaseModel):
    company_name: str = Field(min_length=2)
    owner_email: EmailStr
    owner_name: str
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)
    role: UserRole = UserRole.staff


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True
