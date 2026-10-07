COMPOSE=docker compose
PYTHON ?= python

define verify_url
	@attempt=0; \
	until curl -fsS --max-time 2 "$(1)" >/dev/null 2>&1; do \
		attempt=$$((attempt + 1)); \
		if [ $$attempt -ge 30 ]; then \
			echo "ERROR: $(2) chưa sẵn sàng sau 30 lần thử: $(1)" >&2; \
			exit 1; \
		fi; \
		sleep 2; \
	done
endef

.PHONY: up down ps logs build test verify evidence clean

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down -v

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs --tail=100

build:
	$(COMPOSE) build

test:
	OIDC_ISSUER=http://localhost:8080/realms/ecommerce \
	OIDC_INTERNAL_URL=http://keycloak:8080/realms/ecommerce \
	OIDC_AUDIENCE=app1-api \
	PYTHONPATH=ma-nguon/resource-server \
	$(PYTHON) -m unittest discover -s ma-nguon/resource-server/tests -v

verify:
	@echo "=== Kiem tra Keycloak ==="
	$(call verify_url,http://127.0.0.1:8080/realms/ecommerce/.well-known/openid-configuration,Keycloak)
	@echo "Keycloak: OK"

	@echo "=== Kiem tra Resource Server 1 ==="
	$(call verify_url,http://127.0.0.1:8001/health,Resource Server 1)
	@echo "Resource Server 1: OK"

	@echo "=== Kiem tra Resource Server 2 ==="
	$(call verify_url,http://127.0.0.1:8002/health,Resource Server 2)
	@echo "Resource Server 2: OK"

	@echo "=== Kiem tra Resource Server 3 ==="
	$(call verify_url,http://127.0.0.1:8003/health,Resource Server 3)
	@echo "Resource Server 3: OK"

	$(MAKE) evidence
	@echo "M3 security evidence: PASS"
	@echo "M2 verification: PASS"

evidence:
	$(PYTHON) scripts/export_filtered_realm.py
	@echo "Filtered Keycloak realm export: bang-chung/realm-export-filtered.json"

clean:
	$(COMPOSE) down -v --remove-orphans