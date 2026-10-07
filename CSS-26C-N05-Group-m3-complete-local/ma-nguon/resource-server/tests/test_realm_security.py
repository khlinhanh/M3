import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
REALM_PATH = ROOT / "cau-hinh" / "keycloak" / "realm.json"


class RealmSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.realm = json.loads(REALM_PATH.read_text(encoding="utf-8"))

    def test_retains_latest_local_realm_and_access_token_defaults(self):
        self.assertEqual(self.realm["realm"], "ecommerce")
        self.assertEqual(self.realm["sslRequired"], "none")
        self.assertEqual(self.realm["accessTokenLifespan"], 300)

    def test_session_and_refresh_token_lifetimes_are_bounded(self):
        self.assertEqual(self.realm["ssoSessionIdleTimeout"], 900)
        self.assertEqual(self.realm["ssoSessionMaxLifespan"], 36000)
        self.assertEqual(self.realm["clientSessionIdleTimeout"], 900)
        self.assertEqual(self.realm["clientSessionMaxLifespan"], 36000)
        self.assertIs(self.realm["revokeRefreshToken"], True)
        self.assertEqual(self.realm["refreshTokenMaxReuse"], 0)

    def test_self_service_password_recovery_is_disabled_and_brute_force_protected(self):
        self.assertIs(self.realm["resetPasswordAllowed"], False)
        self.assertIs(self.realm["bruteForceProtected"], True)
        self.assertEqual(self.realm["failureFactor"], 5)

    def test_all_applications_keep_distinct_audiences_and_pkce(self):
        clients = {client["clientId"]: client for client in self.realm["clients"]}
        for app_id, api_id in (
            ("app1", "app1-api"),
            ("app2", "app2-api"),
            ("app3", "app3-api"),
        ):
            with self.subTest(application=app_id):
                client = clients[app_id]
                self.assertEqual(
                    client["attributes"]["pkce.code.challenge.method"],
                    "S256",
                )
                self.assertFalse(client["directAccessGrantsEnabled"])
                audiences = {
                    mapper["config"]["included.client.audience"]
                    for mapper in client["protocolMappers"]
                    if mapper["protocolMapper"] == "oidc-audience-mapper"
                    and mapper["config"].get("access.token.claim") == "true"
                }
                self.assertIn(api_id, audiences)

    def test_browser_flow_requires_totp_only_for_admin_role(self):
        flows = {flow["alias"]: flow for flow in self.realm["authenticationFlows"]}
        self.assertEqual(self.realm["browserFlow"], "Browser with admin TOTP")
        browser = flows["Browser with admin TOTP"]
        forms = flows["Browser login forms"]
        admin_totp = flows["Admin TOTP"]
        self.assertTrue(browser["topLevel"])

        form_subflow = next(
            execution
            for execution in browser["authenticationExecutions"]
            if execution.get("flowAlias") == "Browser login forms"
        )
        self.assertEqual(form_subflow["requirement"], "ALTERNATIVE")
        conditional_mfa = next(
            execution
            for execution in forms["authenticationExecutions"]
            if execution.get("flowAlias") == "Admin TOTP"
        )
        self.assertEqual(conditional_mfa["requirement"], "CONDITIONAL")

        role_check = next(
            execution
            for execution in admin_totp["authenticationExecutions"]
            if execution.get("authenticator") == "conditional-user-role"
        )
        otp = next(
            execution
            for execution in admin_totp["authenticationExecutions"]
            if execution.get("authenticator") == "auth-otp-form"
        )
        self.assertEqual(role_check["requirement"], "REQUIRED")
        self.assertEqual(role_check["authenticatorConfig"], "admin-role-condition")
        self.assertEqual(otp["requirement"], "REQUIRED")
        self.assertTrue(otp["userSetupAllowed"])

        role_config = next(
            item["config"]
            for item in self.realm["authenticatorConfig"]
            if item["alias"] == "admin-role-condition"
        )
        self.assertEqual(role_config["condUserRole"], "admin")
        self.assertEqual(role_config["negate"], "false")

    def test_totp_policy_is_six_digit_thirty_second_totp(self):
        self.assertEqual(self.realm["otpPolicyType"], "totp")
        self.assertEqual(self.realm["otpPolicyDigits"], 6)
        self.assertEqual(self.realm["otpPolicyPeriod"], 30)
        self.assertFalse(self.realm["otpPolicyCodeReusable"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
