from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey('companies.id', ondelete='CASCADE'), index=True)
    stripe_customer_id: Mapped[str] = mapped_column(String(255), index=True)
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), index=True)
    plan: Mapped[str] = mapped_column(String(64), default='free')
    status: Mapped[str] = mapped_column(String(64), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company = relationship('Company', back_populates='subscriptions')
