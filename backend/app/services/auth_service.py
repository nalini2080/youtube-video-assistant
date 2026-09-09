from typing import Optional

from fastapi import Request, HTTPException
from clerk_backend_api import Clerk
from clerk_backend_api.security import authenticate_request
from clerk_backend_api.security.types import AuthenticateRequestOptions
import logging; logger = logging.getLogger(__name__)

from app.config import settings

_clerk_client: Optional[Clerk] = None


def _get_clerk_client() -> Clerk:
    global _clerk_client
    if _clerk_client is None:
        if not settings.clerk_secret_key:
            raise RuntimeError("CLERK_SECRET_KEY is not configured on the backend")
        _clerk_client = Clerk(bearer_auth=settings.clerk_secret_key)
    return _clerk_client


async def get_optional_user_id(request: Request) -> Optional[str]:
    """
    Returns the signed-in user's Clerk ID if a valid session token is
    present on the request, or None otherwise. Never raises — this lets a
    route serve both signed-in and anonymous users, with the route itself
    deciding what (if anything) to do differently for each.
    """
    if not settings.clerk_secret_key:
        return None

    try:
        client = _get_clerk_client()
        request_state = client.authenticate_request(
            request,
            AuthenticateRequestOptions(authorized_parties=settings.frontend_origins_list),
        )
    except Exception as exc:
        logger.warning(f"Clerk auth check failed: {exc}")
        return None
    except Exception:
        return None

    if not request_state.is_signed_in:
        return None

    return request_state.payload.get("sub")


async def require_user_id(request: Request) -> str:
    """Same check as get_optional_user_id, but raises 401 if not signed in."""
    user_id = await get_optional_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Sign in required for this action.")
    return user_id