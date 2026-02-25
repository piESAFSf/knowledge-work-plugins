from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
import stripe

from app.core.config import settings
from app.core.database import get_db
from app.models import Company, Conversation
from app.services.ai_service import summarize_message
from app.services.line_service import validate_line_signature
from app.services.stripe_service import parse_subscription_event

router = APIRouter(prefix='/webhooks', tags=['webhooks'])


@router.post('/stripe')
async def stripe_webhook(request: Request, db: Session = Depends(get_db), stripe_signature: str = Header(alias='Stripe-Signature')):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.stripe_webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail='Invalid Stripe signature') from exc

    if event['type'] in {'customer.subscription.created', 'customer.subscription.updated'}:
        plan, quota = parse_subscription_event(event)
        customer = event['data']['object']['customer']
        company = db.query(Company).filter(Company.stripe_customer_id == customer).first()
        if company:
            company.subscription_plan = plan
            company.monthly_quota = quota
            db.commit()

    return {'received': True}


@router.post('/line')
async def line_webhook(request: Request, db: Session = Depends(get_db), x_line_signature: str = Header(alias='X-Line-Signature')):
    body = await request.body()
    if not validate_line_signature(body, x_line_signature):
        raise HTTPException(status_code=400, detail='Invalid LINE signature')

    data = await request.json()
    for event in data.get('events', []):
        text = event.get('message', {}).get('text', '')
        line_user_id = event.get('source', {}).get('userId')
        if not line_user_id:
            continue
        company = db.query(Company).filter(Company.line_user_id == line_user_id).first()
        if not company:
            continue
        if company.used_quota >= company.monthly_quota:
            continue
        summary = await summarize_message(text)
        company.used_quota += 1
        db.add(Conversation(company_id=company.id, input_text=text, output_text=summary, source='line'))
    db.commit()
    return {'ok': True}
