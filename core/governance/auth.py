"""Signed short-lived HMAC bearer tokens."""
from __future__ import annotations
import base64, hashlib, hmac, json, os, secrets, time
from dataclasses import dataclass
from typing import Any
from core.governance.authority import Role

class AuthenticationError(ValueError):
    pass

@dataclass(frozen=True)
class TokenClaims:
    subject: str
    role: Role
    expires_at: int

def _enc(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

def _dec(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))

def get_token_secret() -> bytes:
    value = os.getenv("VISION_INFINIE_TOKEN_SECRET", "")
    if len(value.encode("utf-8")) < 32:
        raise RuntimeError("VISION_INFINIE_TOKEN_SECRET must contain at least 32 characters.")
    return value.encode("utf-8")

def issue_token(subject: str, role: Role | str, secret: bytes, ttl_seconds: int = 3600) -> str:
    subject = subject.strip()
    try:
        role = Role(role)
    except ValueError as exc:
        raise ValueError("Role must be founder, director, or agent.") from exc
    if not subject or len(subject) > 120:
        raise ValueError("Subject must contain between 1 and 120 characters.")
    if len(secret) < 32:
        raise ValueError("Signing secret must contain at least 32 bytes.")
    if not 60 <= ttl_seconds <= 86400:
        raise ValueError("Token lifetime must be between 60 and 86400 seconds.")
    now = int(time.time())
    payload = {"sub": subject, "role": role.value, "iat": now, "exp": now + ttl_seconds, "jti": secrets.token_urlsafe(12)}
    encoded = _enc(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).digest()
    return encoded + "." + _enc(signature)

def verify_token(token: str, secret: bytes, now: int | None = None) -> TokenClaims:
    if not token or len(token) > 4096 or token.count(".") != 1:
        raise AuthenticationError("Invalid bearer token.")
    encoded, supplied = token.split(".", 1)
    expected = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).digest()
    try:
        actual = _dec(supplied)
    except Exception as exc:
        raise AuthenticationError("Invalid bearer token.") from exc
    if not hmac.compare_digest(expected, actual):
        raise AuthenticationError("Invalid bearer token.")
    try:
        payload: dict[str, Any] = json.loads(_dec(encoded))
        subject, role = payload["sub"], Role(payload["role"])
        issued, expires = int(payload["iat"]), int(payload["exp"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AuthenticationError("Invalid bearer token.") from exc
    current = int(time.time()) if now is None else now
    if not isinstance(subject, str) or not subject or issued > current + 30 or expires <= current or expires - issued > 86400:
        raise AuthenticationError("Expired or invalid bearer token.")
    return TokenClaims(subject, role, expires)

def authenticate_header(header: str | None, secret: bytes) -> TokenClaims:
    if not header:
        raise AuthenticationError("Bearer token required.")
    scheme, separator, token = header.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise AuthenticationError("Bearer token required.")
    return verify_token(token.strip(), secret)
