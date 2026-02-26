from pydantic import BaseModel


class CompanyResponse(BaseModel):
    id: int
    name: str
    quota_limit: int

    class Config:
        from_attributes = True
