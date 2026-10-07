import time
import unittest
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

import app


ISSUER = "http://localhost:8080/realms/ecommerce"
AUDIENCE = "app1-api"
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)
PUBLIC_JWK = jwt.algorithms.RSAAlgorithm.to_jwk(
    PRIVATE_KEY.public_key(),
    as_dict=True,
)
PUBLIC_JWK["kid"] = "test-key"


def make_token(
    *,
    audience=AUDIENCE,
    issuer=ISSUER,
    expiration=None,
    not_before=None,
    key=PRIVATE_KEY,
    algorithm="RS256",
    omit_claims=(),
):
    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": "test-subject",
        "iat": now,
        "exp": expiration if expiration is not None else now + 120,
        "realm_access": {"roles": ["user"]},
    }
    if not_before is not None:
        payload["nbf"] = not_before
    for claim in omit_claims:
        payload.pop(claim, None)
    headers = {"kid": "test-key"} if algorithm != "none" else None
    if algorithm == "none":
        signing_key = None
    elif algorithm == "HS256":
        signing_key = "test-secret"
    else:
        signing_key = key
    return jwt.encode(
        payload,
        signing_key,
        algorithm=algorithm,
        headers=headers,
    )


class TokenVerificationTests(unittest.TestCase):
    def verify_token(self, token):
        with patch.object(
            app,
            "get_jwks",
            return_value={"keys": [PUBLIC_JWK]},
        ):
            return app.verify_access_token(token)

    def assert_rejected(self, token):
        with self.assertRaises(HTTPException) as raised:
            self.verify_token(token)
        self.assertEqual(raised.exception.status_code, 401)

    def test_accepts_valid_token(self):
        claims = self.verify_token(make_token())
        self.assertEqual(claims["sub"], "test-subject")

    def test_rejects_alg_none(self):
        self.assert_rejected(make_token(algorithm="none"))

    def test_rejects_wrong_audience(self):
        self.assert_rejected(make_token(audience="app2-api"))

    def test_rejects_app3_audience(self):
        self.assert_rejected(make_token(audience="app3-api"))

    def test_rejects_wrong_issuer(self):
        self.assert_rejected(make_token(issuer="https://attacker.invalid"))

    def test_rejects_expired_token(self):
        self.assert_rejected(
            make_token(expiration=int(time.time()) - 60)
        )

    def test_rejects_token_not_yet_valid(self):
        self.assert_rejected(
            make_token(not_before=int(time.time()) + 60)
        )

    def test_rejects_invalid_signature(self):
        self.assert_rejected(make_token(key=OTHER_PRIVATE_KEY))

    def test_rejects_unsupported_hmac_algorithm(self):
        self.assert_rejected(make_token(algorithm="HS256"))

    def test_rejects_malformed_token(self):
        self.assert_rejected("not-a-jwt")

    def test_rejects_missing_issuer(self):
        self.assert_rejected(make_token(omit_claims=("iss",)))

    def test_rejects_missing_audience(self):
        self.assert_rejected(make_token(omit_claims=("aud",)))

    def test_rejects_missing_expiration(self):
        self.assert_rejected(make_token(omit_claims=("exp",)))

    def test_rejects_missing_issued_at(self):
        self.assert_rejected(make_token(omit_claims=("iat",)))

    def test_rejects_unknown_signing_key(self):
        token = make_token()
        header = jwt.get_unverified_header(token)
        header["kid"] = "unknown-key"
        tampered = jwt.encode(
            jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False,
                    "verify_aud": False,
                    "verify_iss": False,
                },
            ),
            PRIVATE_KEY,
            algorithm="RS256",
            headers=header,
        )
        self.assert_rejected(tampered)

    def test_rejects_missing_authorization_header(self):
        with self.assertRaises(HTTPException) as raised:
            app.get_current_user(None)
        self.assertEqual(raised.exception.status_code, 401)

    def test_rejects_non_bearer_authorization(self):
        with self.assertRaises(HTTPException) as raised:
            app.get_current_user("Basic dXNlcjpwYXNz")
        self.assertEqual(raised.exception.status_code, 401)

    def test_rejects_empty_bearer_token(self):
        with self.assertRaises(HTTPException) as raised:
            app.get_current_user("Bearer   ")
        self.assertEqual(raised.exception.status_code, 401)

    def test_user_role_can_access_user_api(self):
        with patch.object(
            app,
            "verify_access_token",
            return_value={"sub": "user-1", "realm_access": {"roles": ["user"]}},
        ):
            response = app.user_api("Bearer valid-token")
        self.assertEqual(response["sub"], "user-1")
        self.assertIn("user", response["roles"])

    def test_user_without_role_is_denied_user_api(self):
        with patch.object(
            app,
            "verify_access_token",
            return_value={"sub": "unknown", "realm_access": {"roles": []}},
        ):
            with self.assertRaises(HTTPException) as raised:
                app.user_api("Bearer valid-token")
        self.assertEqual(raised.exception.status_code, 403)

    def test_user_role_is_denied_admin_api(self):
        with patch.object(
            app,
            "verify_access_token",
            return_value={"sub": "user-1", "realm_access": {"roles": ["user"]}},
        ):
            with self.assertRaises(HTTPException) as raised:
                app.admin_api("Bearer valid-token")
        self.assertEqual(raised.exception.status_code, 403)

    def test_admin_role_can_access_admin_api(self):
        with patch.object(
            app,
            "verify_access_token",
            return_value={"sub": "admin-1", "realm_access": {"roles": ["admin"]}},
        ):
            response = app.admin_api("Bearer valid-token")
        self.assertEqual(response["sub"], "admin-1")
        self.assertIn("admin", response["roles"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
