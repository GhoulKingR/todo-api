import base64
import hmac
import hashlib
import secrets
import json
import time

# Secret key for signing and verifying tokens
SECRET_KEY = secrets.token_bytes(32).hex()


def base64_encode(data: str) -> str:
    encoded = base64.urlsafe_b64encode(data.encode()).decode()
    return encoded.rstrip("=")


def base64_decode(data: str) -> str:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding).decode()


def create_signature(encoded_header: str, encoded_payload: str) -> str:
    message = f"{encoded_header}.{encoded_payload}".encode()
    key = bytes.fromhex(SECRET_KEY)
    signature = hmac.new(key, message, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode().rstrip("=")


def generate_token(payload: dict, expires_in: int = 3600) -> str:
    if not isinstance(payload, dict) or payload is None:
        raise ValueError("Payload must be a non-null dictionary")

    header = {"alg": "HS256", "typ": "JWT"}

    payload_copy = payload.copy()
    payload_copy["exp"] = int(time.time()) + expires_in

    encoded_header = base64_encode(json.dumps(header))
    encoded_payload = base64_encode(json.dumps(payload_copy))

    signature = create_signature(encoded_header, encoded_payload)

    return f"{encoded_header}.{encoded_payload}.{signature}"


def validate_token(token: str) -> dict:
    if not isinstance(token, str):
        raise ValueError("Invalid token format")

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token structure")

    encoded_header, encoded_payload, signature = parts
    expected_signature = create_signature(encoded_header, encoded_payload)

    if not hmac.compare_digest(expected_signature, signature):
        raise ValueError("Invalid token signature")

    payload = json.loads(base64_decode(encoded_payload))

    if "exp" in payload and payload["exp"] < int(time.time()):
        raise ValueError("Token has expired")

    return payload
