from pydantic import BaseModel


class UsageStats(BaseModel):
    plan: str
    monthly_quota: int
    used_quota: int
    remaining_quota: int
    conversation_count: int
