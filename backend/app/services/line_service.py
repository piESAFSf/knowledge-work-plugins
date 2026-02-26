import hmac
import hashlib
import base64

from app.core.config import settings


def verify_line_signature(body: bytes, signature: str) -> bool:
    digest = hmac.new(settings.line_channel_secret.encode(), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)
