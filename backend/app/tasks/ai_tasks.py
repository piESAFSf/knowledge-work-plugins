import asyncio

from app.core.database import SessionLocal
from app.models.conversation import Conversation
from app.models.usage import UsageRecord
from app.services.openai_service import OpenAIService
from app.tasks.celery_app import celery_app


@celery_app.task(name='tasks.process_conversation')
def process_conversation(conversation_id: int) -> None:
    db = SessionLocal()
    try:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            return
        summary = asyncio.run(OpenAIService().summarize(conv.message))
        conv.ai_summary = summary
        db.add(UsageRecord(company_id=conv.company_id, metric='ai_calls', amount=1))
        db.commit()
    finally:
        db.close()
