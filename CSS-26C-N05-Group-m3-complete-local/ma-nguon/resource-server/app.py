import os
from typing import Dict, Any

import jwt
import requests

from fastapi import FastAPI, Header, HTTPException


app = FastAPI()


# Issuer phải khớp chính xác với "iss" trong access token.
# Ví dụ:
# http://localhost:8080/realms/ecommerce
OIDC_ISSUER = os.environ["OIDC_ISSUER"]

# URL nội bộ Docker dùng để Resource Server lấy
# OpenID configuration và JWKS từ Keycloak.
# Ví dụ:
# http://keycloak:8080/realms/ecommerce
OIDC_INTERNAL_URL = os.environ.get(
    "OIDC_INTERNAL_URL",
    OIDC_ISSUER
)

OIDC_AUDIENCE = os.environ["OIDC_AUDIENCE"]


OIDC_CONFIG_URL = (
    f"{OIDC_INTERNAL_URL}/.well-known/openid-configuration"
)


def get_oidc_config() -> Dict[str, Any]:
    response = requests.get(
        OIDC_CONFIG_URL,
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def get_jwks():
    config = get_oidc_config()

    # Keycloak discovery có thể trả jwks_uri là
    # localhost, trong khi Resource Server chạy trong Docker.
    # Thay hostname localhost bằng keycloak để container
    # có thể truy cập được Keycloak.
    jwks_uri = config["jwks_uri"]

    if jwks_uri.startswith("http://localhost:8080"):
        jwks_uri = jwks_uri.replace(
            "http://localhost:8080",
            "http://keycloak:8080",
            1
        )

    response = requests.get(
        jwks_uri,
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def verify_access_token(token: str) -> Dict[str, Any]:

    try:
        jwks = get_jwks()

        header = jwt.get_unverified_header(token)

        if header.get("alg") != "RS256":
            raise HTTPException(
                status_code=401,
                detail="Invalid JWT algorithm"
            )

        key = None

        for jwk in jwks["keys"]:
            if jwk["kid"] == header.get("kid"):
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break

        if key is None:
            raise HTTPException(
                status_code=401,
                detail="Unknown signing key"
            )

        payload = jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            issuer=OIDC_ISSUER,
            audience=OIDC_AUDIENCE,
            options={
                "require": [
                    "iss",
                    "aud",
                    "exp",
                    "iat"
                ]
            }
        )

        return payload

    except HTTPException:
        raise

    except Exception as e:
        print(
            "JWT VERIFY ERROR:",
            repr(e),
            flush=True
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )


def get_current_user(
    authorization: str | None
) -> Dict[str, Any]:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header"
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Empty access token"
        )

    return verify_access_token(token)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/api/user")
def user_api(
    authorization: str | None = Header(default=None)
):

    claims = get_current_user(authorization)

    roles = claims.get(
        "realm_access",
        {}
    ).get(
        "roles",
        []
    )

    if "user" not in roles and "admin" not in roles:
        raise HTTPException(
            status_code=403,
            detail="Insufficient role"
        )

    return {
        "message": "User API access granted",
        "sub": claims.get("sub"),
        "roles": roles
    }


@app.get("/api/admin")
def admin_api(
    authorization: str | None = Header(default=None)
):

    claims = get_current_user(authorization)

    roles = claims.get(
        "realm_access",
        {}
    ).get(
        "roles",
        []
    )

    if "admin" not in roles:
        raise HTTPException(
            status_code=403,
            detail="Admin role required"
        )

    return {
        "message": "Admin API access granted",
        "sub": claims.get("sub"),
        "roles": roles
    }