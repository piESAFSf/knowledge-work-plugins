import stripe

from app.core.config import settings

stripe.api_key = settings.stripe_api_key

PLAN_MAP = {
    'price_basic': ('basic', 10000),
    'price_pro': ('pro', 100000),
}


def parse_subscription_event(event: dict) -> tuple[str, int]:
    price_id = event['data']['object']['items']['data'][0]['price']['id']
    return PLAN_MAP.get(price_id, ('free', 1000))
