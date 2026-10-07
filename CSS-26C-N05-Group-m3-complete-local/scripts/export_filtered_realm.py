import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cau-hinh" / "keycloak" / "realm.json"
DESTINATION = ROOT / "bang-chung" / "realm-export-filtered.json"
SECRET_FIELDS = {"secret", "clientSecret", "client_secret"}
CREDENTIAL_SECRET_FIELDS = {"value", "hashedSaltedValue", "salt"}


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def redact_secrets(value, in_credentials=False):
    if isinstance(value, list):
        return [redact_secrets(item, in_credentials) for item in value]
    if not isinstance(value, dict):
        return value

    redacted = {}
    for key, child in value.items():
        if key in SECRET_FIELDS or (
            in_credentials and key in CREDENTIAL_SECRET_FIELDS
        ):
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = redact_secrets(
                child,
                in_credentials=(key == "credentials"),
            )
    return redacted


def find_execution(flow, *, provider_id=None, flow_alias=None):
    for execution in flow.get("authenticationExecutions", []):
        if provider_id and execution.get("authenticator") == provider_id:
            return execution
        if flow_alias and execution.get("flowAlias") == flow_alias:
            return execution
    return None


def validate_realm(realm):
    if realm.get("realm") != "ecommerce":
        raise ValueError("Unexpected realm name")
    if realm.get("enabled") is not True:
        raise ValueError("Realm must be enabled")
    if realm.get("sslRequired") != "none":
        raise ValueError("Keep the supplied local-development SSL setting")
    if realm.get("accessTokenLifespan") != 300:
        raise ValueError("Keep the supplied five-minute access-token lifetime")
    for field, expected in (
        ("ssoSessionIdleTimeout", 900),
        ("ssoSessionMaxLifespan", 36000),
        ("clientSessionIdleTimeout", 900),
        ("clientSessionMaxLifespan", 36000),
    ):
        if realm.get(field) != expected:
            raise ValueError(f"{field} must be {expected} seconds")
    if realm.get("revokeRefreshToken") is not True:
        raise ValueError("Refresh-token rotation must be enabled")
    if realm.get("refreshTokenMaxReuse") != 0:
        raise ValueError("Refresh tokens must not be reusable")
    if realm.get("resetPasswordAllowed") is not False:
        raise ValueError("Self-service password reset must remain disabled")
    if realm.get("bruteForceProtected") is not True:
        raise ValueError("Brute-force protection must be enabled")
    if realm.get("failureFactor") != 5:
        raise ValueError("The configured failure threshold must remain five")
    if realm.get("otpPolicyType") != "totp":
        raise ValueError("Realm must use TOTP")
    if realm.get("otpPolicyDigits") != 6 or realm.get("otpPolicyPeriod") != 30:
        raise ValueError("TOTP policy must use six digits every 30 seconds")

    roles = {item["name"] for item in realm.get("roles", {}).get("realm", [])}
    if roles != {"user", "admin"}:
        raise ValueError("Realm must contain exactly the user and admin roles")

    clients = {client["clientId"]: client for client in realm.get("clients", [])}
    required_clients = {
        "app1",
        "app2",
        "app3",
        "app1-api",
        "app2-api",
        "app3-api",
    }
    if not required_clients.issubset(clients):
        raise ValueError("Realm must retain all three OIDC apps and API clients")

    for application, api in (
        ("app1", "app1-api"),
        ("app2", "app2-api"),
        ("app3", "app3-api"),
    ):
        client = clients[application]
        if client.get("publicClient") is not True:
            raise ValueError(f"{application} must remain a public OIDC client")
        if client.get("standardFlowEnabled") is not True:
            raise ValueError(f"{application} must use the OIDC authorization flow")
        if client.get("directAccessGrantsEnabled") is not False:
            raise ValueError(f"{application} must keep password grants disabled")
        if client.get("attributes", {}).get("pkce.code.challenge.method") != "S256":
            raise ValueError(f"{application} must require PKCE S256")
        audiences = {
            mapper.get("config", {}).get("included.client.audience")
            for mapper in client.get("protocolMappers", [])
            if mapper.get("protocolMapper") == "oidc-audience-mapper"
            and mapper.get("config", {}).get("access.token.claim") == "true"
        }
        if api not in audiences:
            raise ValueError(f"{application} must emit audience {api}")

    for api in ("app1-api", "app2-api", "app3-api"):
        if clients[api].get("bearerOnly") is not True:
            raise ValueError(f"{api} must remain a bearer-only resource client")

    flow_alias = "Browser with admin TOTP"
    if realm.get("browserFlow") != flow_alias:
        raise ValueError("Browser login must use the supplied admin-TOTP flow")
    flows = {flow["alias"]: flow for flow in realm.get("authenticationFlows", [])}
    browser = flows.get(flow_alias)
    forms = flows.get("Browser login forms")
    admin_totp = flows.get("Admin TOTP")
    if not browser or browser.get("topLevel") is not True:
        raise ValueError("Admin-TOTP browser flow must be the active top-level flow")
    if not forms or not admin_totp:
        raise ValueError("Admin-TOTP conditional subflows are missing")
    if not find_execution(browser, flow_alias="Browser login forms"):
        raise ValueError("Browser flow must retain the username/password form")
    conditional = find_execution(forms, flow_alias="Admin TOTP")
    if not conditional or conditional.get("requirement") != "CONDITIONAL":
        raise ValueError("TOTP subflow must be conditional")
    role_check = find_execution(
        admin_totp,
        provider_id="conditional-user-role",
    )
    if (
        not role_check
        or role_check.get("requirement") != "REQUIRED"
        or role_check.get("authenticatorConfig") != "admin-role-condition"
    ):
        raise ValueError("TOTP condition must check the admin role")
    role_config = next(
        (
            item.get("config", {})
            for item in realm.get("authenticatorConfig", [])
            if item.get("alias") == "admin-role-condition"
        ),
        None,
    )
    if (
        not role_config
        or role_config.get("condUserRole") != "admin"
        or role_config.get("negate") != "false"
    ):
        raise ValueError("Role condition must match, not negate, admin")
    otp = find_execution(admin_totp, provider_id="auth-otp-form")
    if (
        not otp
        or otp.get("requirement") != "REQUIRED"
        or otp.get("userSetupAllowed") is not True
    ):
        raise ValueError("Admin OTP must be required and setup must be allowed")


def main() -> None:
    realm = json.loads(
        SOURCE.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
    )
    validate_realm(realm)
    filtered = redact_secrets(realm)

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(
        json.dumps(filtered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Security configuration checks: PASS "
        "(OIDC clients, PKCE/audience, admin-only TOTP, sessions, recovery)"
    )


if __name__ == "__main__":
    main()
