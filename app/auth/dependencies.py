# """JWT verification and authorization dependencies.

# This module supports TWO verification modes:

# 1. DEV MODE (default when JWKS unreachable):
#    - Verifies JWT using BETTER_AUTH_SECRET with HS256
#    - Fast, no network dependency
#    - Requires secret to match frontend Better Auth config

# 2. PRODUCTION MODE (when JWKS is reachable):
#    - Fetches public keys from Better Auth JWKS endpoint
#    - Verifies using asymmetric keys (EdDSA/RS256)
#    - More secure, standard OAuth2/OIDC approach

# The module automatically falls back to dev mode if JWKS fetch fails.
# """

# import os
# from typing import Annotated

# import jwt
# from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# from app.core.config import settings

# # Use HTTPBearer for token extraction
# security = HTTPBearer(auto_error=False)

# # Environment flag for auth mode
# # Set AUTH_MODE=jwks to force JWKS verification (production)
# # Default is "secret" which uses HS256 with BETTER_AUTH_SECRET
# AUTH_MODE = os.getenv("AUTH_MODE", "secret")


# def verify_token_with_secret(token: str) -> dict:
#     """Verify JWT using shared secret (HS256).

#     This is the DEV MODE verification method.
#     Uses BETTER_AUTH_SECRET which must match the frontend.

#     Args:
#         token: The JWT string

#     Returns:
#         Decoded token payload

#     Raises:
#         InvalidTokenError: If token is invalid or signature fails
#     """
#     return jwt.decode(
#         token,
#         settings.better_auth_secret,
#         algorithms=["HS256"],
#         options={
#             "verify_aud": False,
#             "verify_iss": False,
#         },
#         leeway=30,
#     )


# def verify_token_with_jwks(token: str) -> dict:
#     """Verify JWT using JWKS endpoint (asymmetric keys).

#     This is the PRODUCTION MODE verification method.
#     Fetches public keys from Better Auth's JWKS endpoint.

#     Args:
#         token: The JWT string

#     Returns:
#         Decoded token payload

#     Raises:
#         Exception: If JWKS fetch fails or signature verification fails
#     """
#     from jwt import PyJWKClient

#     jwks_url = f"{settings.better_auth_base_url}/api/auth/.well-known/jwks.json"
#     jwks_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=300)
#     signing_key = jwks_client.get_signing_key_from_jwt(token)

#     return jwt.decode(
#         token,
#         signing_key.key,
#         algorithms=["EdDSA", "ES256", "RS256", "PS256"],
#         options={"verify_aud": False},
#         leeway=30,
#     )


# async def get_current_user_id(
#     credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]
# ) -> str:
#     """Extract and verify user ID from Better Auth JWT.

#     Verification strategy:
#     1. If AUTH_MODE=secret (default): Use HS256 with shared secret
#     2. If AUTH_MODE=jwks: Try JWKS first, fall back to secret on network error

#     Returns:
#         User ID from JWT 'sub' claim

#     Raises:
#         HTTPException 401: If token is missing, invalid, or expired
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     if credentials is None:
#         print("[Auth] No credentials provided")
#         raise credentials_exception

#     token = credentials.credentials
#     if not token:
#         print("[Auth] Empty token")
#         raise credentials_exception

#     print(f"[Auth] Verifying token (mode={AUTH_MODE})")
#     print(f"[Auth] Token preview: {token[:50]}..." if len(token) > 50 else f"[Auth] Token: {token}")

#     try:
#         # First, decode without verification to see claims
#         unverified = jwt.decode(token, options={"verify_signature": False})
#         print(f"[Auth] Unverified claims: sub={unverified.get('sub')}, exp={unverified.get('exp')}")

#         # Now verify based on mode
#         if AUTH_MODE == "jwks":
#             try:
#                 payload = verify_token_with_jwks(token)
#                 print("[Auth] JWKS verification successful")
#             except Exception as e:
#                 print(f"[Auth] JWKS verification failed: {e}")
#                 print("[Auth] Falling back to secret verification")
#                 payload = verify_token_with_secret(token)
#                 print("[Auth] Secret verification successful (fallback)")
#         else:
#             # Default: use secret verification (fast, no network)
#             payload = verify_token_with_secret(token)
#             print("[Auth] Secret verification successful")

#         user_id: str | None = payload.get("sub")

#         if not user_id:
#             print("[Auth] Token missing 'sub' claim")
#             raise credentials_exception

#         print(f"[Auth] Authenticated user: {user_id}")
#         return user_id

#     except ExpiredSignatureError:
#         print("[Auth] Token expired")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except DecodeError as e:
#         print(f"[Auth] Decode error: {e}")
#         raise credentials_exception
#     except InvalidTokenError as e:
#         print(f"[Auth] Invalid token: {e}")
#         raise credentials_exception
#     except Exception as e:
#         print(f"[Auth] Unexpected error: {type(e).__name__}: {e}")
#         raise credentials_exception


# # Type alias for dependency injection
# CurrentUserId = Annotated[str, Depends(get_current_user_id)]





# """
# JWT verification and authorization dependencies.

# Supports TWO verification modes:

# 1. DEV MODE (default / AUTH_MODE=secret)
#    - HS256 using BETTER_AUTH_SECRET
#    - Fast, no network dependency

# 2. PRODUCTION MODE (AUTH_MODE=jwks)
#    - Verifies using Better Auth JWKS
#    - Falls back to secret if JWKS fails

# IMPORTANT:
# - CORS preflight (OPTIONS) requests are allowed without auth
# """

# import os
# from typing import Annotated

# import jwt
# from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, DecodeError
# from fastapi import Depends, HTTPException, status, Request
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# from app.core.config import settings

# # Extract Bearer token safely (do NOT auto-throw on missing header)
# security = HTTPBearer(auto_error=False)

# # Auth mode: "secret" (default) or "jwks"
# AUTH_MODE = os.getenv("AUTH_MODE", "secret")


# def verify_token_with_secret(token: str) -> dict:
#     """Verify JWT using shared secret (HS256)."""
#     return jwt.decode(
#         token,
#         settings.better_auth_secret,
#         algorithms=["HS256"],
#         options={
#             "verify_aud": False,
#             "verify_iss": False,
#         },
#         leeway=30,
#     )


# def verify_token_with_jwks(token: str) -> dict:
#     """Verify JWT using Better Auth JWKS."""
#     from jwt import PyJWKClient

#     jwks_url = f"{settings.better_auth_base_url}/api/auth/.well-known/jwks.json"
#     jwks_client = PyJWKClient(jwks_url, cache_keys=True, lifespan=300)
#     signing_key = jwks_client.get_signing_key_from_jwt(token)

#     return jwt.decode(
#         token,
#         signing_key.key,
#         algorithms=["EdDSA", "ES256", "RS256", "PS256"],
#         options={"verify_aud": False},
#         leeway=30,
#     )


# async def get_current_user_id(
#     request: Request,
#     credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
# ) -> str | None:
#     """
#     Extract and verify user ID from JWT.

#     - OPTIONS requests bypass auth (required for CORS)
#     - All other requests require valid JWT
#     """

#     # ✅ VERY IMPORTANT: allow CORS preflight
#     if request.method == "OPTIONS":
#         return None

#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     if credentials is None or not credentials.credentials:
#         raise credentials_exception

#     token = credentials.credentials

#     try:
#         # Decode unverified claims (debug only)
#         unverified = jwt.decode(token, options={"verify_signature": False})
#         user_id = unverified.get("sub")

#         if not user_id:
#             raise credentials_exception

#         # Verify token
#         if AUTH_MODE == "jwks":
#             try:
#                 payload = verify_token_with_jwks(token)
#             except Exception:
#                 payload = verify_token_with_secret(token)
#         else:
#             payload = verify_token_with_secret(token)

#         verified_user_id: str | None = payload.get("sub")

#         if not verified_user_id:
#             raise credentials_exception

#         return verified_user_id

#     except ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     except (DecodeError, InvalidTokenError):
#         raise credentials_exception
#     except Exception:
#         raise credentials_exception


# # Dependency alias
# CurrentUserId = Annotated[str, Depends(get_current_user_id)]


from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings

security = HTTPBearer(auto_error=False)

async def get_current_user_id(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
) -> str | None:
    # ✅ VERY IMPORTANT: allow CORS preflight
    if request.method == "OPTIONS":
        return None

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
            options={
                "verify_aud": False,
                "verify_iss": False,
            },
            leeway=30,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
