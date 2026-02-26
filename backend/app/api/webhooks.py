import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.subscription import Subscription
from app.services.line_service import verify_line_signature
from app.tasks.ai_tasks import process_conversation

router = APIRouter(prefix='/webhooks', tags=['webhooks'])
stripe.api_key = settings.stripe_secret_key


@router.post('/stripe')
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get('stripe-signature', '')
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail='Invalid Stripe signature') from exc

    if event['type'] == 'customer.subscription.updated':
        obj = event['data']['object']
        sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == obj['id']).first()
        if sub:
            sub.status = obj['status']
            sub.plan = (obj.get('items', {}).get('data', [{}])[0].get('price', {}).get('nickname') or 'pro')
            db.commit()
    return {'received': True}


@router.post('/line')
async def line_webhook(
    request: Request,
    x_line_signature: str = Header(default=''),
    db: Session = Depends(get_db),
):
    body = await request.body()
    if not verify_line_signature(body, x_line_signature):
        raise HTTPException(status_code=400, detail='Invalid LINE signature')

    payload = await request.json()
    for event in payload.get('events', []):
        company_id = int(event.get('source', {}).get('groupId', 1))
        message = event.get('message', {}).get('text', '')
        conversation = Conversation(company_id=company_id, source='line', message=message)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        process_conversation.delay(conversation.id)

    return {'ok': True}
