from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Company(BaseModel):
    __tablename__ = 'companies'

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_plan: Mapped[str] = mapped_column(String(50), default='free')
    monthly_quota: Mapped[int] = mapped_column(Integer, default=1000)
    used_quota: Mapped[int] = mapped_column(Integer, default=0)

    users = relationship('User', back_populates='company', cascade='all, delete-orphan')
    conversations = relationship('Conversation', back_populates='company', cascade='all, delete-orphan')
