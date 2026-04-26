import json
import urllib.request
from jwt import PyJWKClient
import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(settings.CLERK_JWKS_URL, cache_keys=True)
    return _jwks_client


def _fetch_clerk_user(clerk_user_id: str) -> dict:
    url = f"https://api.clerk.com/v1/users/{clerk_user_id}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


class ClerkAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header[7:]
        try:
            client = _get_jwks_client()
            signing_key = client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        except Exception as exc:
            raise AuthenticationFailed(f"Invalid Clerk token: {exc}")

        clerk_user_id = payload.get("sub")
        if not clerk_user_id:
            raise AuthenticationFailed("Token missing sub claim")

        user = self._get_or_create_user(clerk_user_id)
        return (user, None)

    def _get_or_create_user(self, clerk_user_id: str):
        from .models import User

        try:
            return User.objects.get(clerk_id=clerk_user_id)
        except User.DoesNotExist:
            pass

        user_data = _fetch_clerk_user(clerk_user_id)
        email_entries = user_data.get("email_addresses", [])
        email = email_entries[0].get("email_address", "") if email_entries else ""
        first_name = user_data.get("first_name") or ""
        last_name = user_data.get("last_name") or ""

        # Link to existing account if same email, otherwise create new
        try:
            user = User.objects.get(email=email)
            user.clerk_id = clerk_user_id
            user.save(update_fields=["clerk_id"])
        except User.DoesNotExist:
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                clerk_id=clerk_user_id,
            )

        return user
