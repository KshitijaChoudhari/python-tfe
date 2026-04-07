.PHONY: help fmt fmt-check lint check test install dev-install type-check clean all venv activate

PYTHON := python3
SRC_DIR := src/pytfe
TEST_DIR := tests
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

help:
	@echo "Available targets:"
	@echo "  venv                  Create virtual environment"
	@echo "  activate              Show command to activate virtual environment"
	@echo "  install               Install package dependencies"
	@echo "  dev-install           Install package and development dependencies"
	@echo "  fmt                   Format code"
	@echo "  fmt-check             Check code formatting"
	@echo "  lint                  Run linting"
	@echo "  check                 Run format check + lint + type check"
	@echo "  type-check            Run type checking"
	@echo "  test                  Run unit tests + all example files"
	@echo "  clean                 Clean build artifacts and cache"
	@echo "  all                   Run clean + dev-install + fmt + lint + test"
	@echo ""
	@echo "Required env vars:"
	@echo "  TFE_TOKEN             API token"
	@echo "  TFE_ORG               Organization name"
	@echo ""
	@echo "Optional env vars (examples skip cleanly if not set):"
	@echo "  TFE_ADDRESS           TFE address (default: https://app.terraform.io)"
	@echo "  TFE_WORKSPACE_ID      Workspace ID"
	@echo "                        -- needed by: configuration_version, notification_configuration,"
	@echo "                                      variables, workspace_resources, state_versions"
	@echo "  TFE_WORKSPACE_NAME    Workspace name"
	@echo "                        -- needed by: notification_configuration, state_versions"
	@echo "  TFE_APPLY_ID          Apply ID        -- needed by: apply"
	@echo "  TFE_PLAN_ID           Plan ID         -- needed by: plan"
	@echo "  TFE_RUN_ID            Run ID          -- needed by: policy_check, run_events"
	@echo "  TFE_TASK_STAGE_ID     Task stage ID   -- needed by: policy_evaluation"
	@echo "  TFE_POLICY_SET_ID     Policy set ID   -- needed by: policy_set_parameter"
	@echo "  TFE_POLICY_NAME       Policy name     -- needed by: policy"
	@echo "  TFE_REG_PROV_NS       Registry provider namespace -- needed by: registry_provider_version"
	@echo "  TFE_REG_PROV_NAME     Registry provider name     -- needed by: registry_provider_version"
	@echo "  SSH_PRIVATE_KEY       SSH private key -- needed by: ssh_keys"
	@echo "  OAUTH_CLIENT_GITHUB_TOKEN  GitHub token (optional, enables GitHub tests in oauth_client)"
	@echo "  WEBHOOK_URL           Webhook URL     -- used by: notification_configuration"
	@echo "  TEAMS_WEBHOOK_URL     Teams URL       -- used by: notification_configuration"

$(VENV)/bin/activate: pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip

venv: $(VENV)/bin/activate

activate:
	@echo "To activate the virtual environment, run:"
	@echo "source $(VENV)/bin/activate"

install: venv
	$(VENV_PIP) install -e .

dev-install: venv
	$(VENV_PIP) install -e ".[dev]"

fmt:
	$(VENV_PYTHON) -m ruff format .
	$(VENV_PYTHON) -m ruff check --fix .

fmt-check:
	$(VENV_PYTHON) -m ruff format --check .
	$(VENV_PYTHON) -m ruff check .

lint:
	$(VENV_PYTHON) -m ruff check .
	$(VENV_PYTHON) -m mypy $(SRC_DIR)

check:
	$(VENV_PYTHON) -m ruff format --check .
	$(VENV_PYTHON) -m ruff check .
	$(VENV_PYTHON) -m mypy $(SRC_DIR)

type-check:
	$(VENV_PYTHON) -m mypy $(SRC_DIR)

test:
	@echo "Checking required environment variables..."
	@if [ -z "$${TFE_TOKEN}" ] || [ -z "$${TFE_ORG}" ]; then \
		echo "ERROR: TFE_TOKEN and TFE_ORG must be set"; \
		exit 1; \
	fi

	@echo ""
	@echo "========================================"
	@echo "Running unit tests..."
	@echo "========================================"
	$(VENV_PYTHON) -m pytest -v tests/

	@echo ""
	@echo "========================================"
	@echo "Running example files..."
	@echo "========================================"

	@echo ""
	@echo "--- agent.py ---"
	-$(VENV_PYTHON) examples/agent.py

	@echo ""
	@echo "--- agent_pool.py ---"
	-$(VENV_PYTHON) examples/agent_pool.py

	@echo ""
	@echo "--- apply.py ---"
	@if [ -z "$${TFE_APPLY_ID}" ]; then \
		echo "SKIPPED: set TFE_APPLY_ID to run apply.py"; \
	else \
		$(VENV_PYTHON) examples/apply.py --apply-id "$${TFE_APPLY_ID}" || true; \
	fi

	@echo ""
	@echo "--- configuration_version.py ---"
	@if [ -z "$${TFE_WORKSPACE_ID}" ]; then \
		echo "SKIPPED: set TFE_WORKSPACE_ID to run configuration_version.py"; \
	else \
		$(VENV_PYTHON) examples/configuration_version.py || true; \
	fi

	@echo ""
	@echo "--- notification_configuration.py ---"
	@if [ -z "$${TFE_WORKSPACE_ID}" ] && [ -z "$${TFE_WORKSPACE_NAME}" ]; then \
		echo "SKIPPED: set TFE_WORKSPACE_ID or TFE_WORKSPACE_NAME to run notification_configuration.py"; \
	else \
		$(VENV_PYTHON) examples/notification_configuration.py || true; \
	fi

	@echo ""
	@echo "--- oauth_client.py ---"
	-$(VENV_PYTHON) examples/oauth_client.py

	@echo ""
	@echo "--- oauth_token.py ---"
	-$(VENV_PYTHON) examples/oauth_token.py

	@echo ""
	@echo "--- org.py ---"
	-$(VENV_PYTHON) examples/org.py

	@echo ""
	@echo "--- organization_membership.py ---"
	-$(VENV_PYTHON) examples/organization_membership.py

	@echo ""
	@echo "--- plan.py ---"
	@if [ -z "$${TFE_PLAN_ID}" ]; then \
		echo "SKIPPED: set TFE_PLAN_ID to run plan.py"; \
	else \
		$(VENV_PYTHON) examples/plan.py --plan-id "$${TFE_PLAN_ID}" || true; \
	fi

	@echo ""
	@echo "--- policy_check.py ---"
	@if [ -z "$${TFE_RUN_ID}" ]; then \
		echo "SKIPPED: set TFE_RUN_ID to run policy_check.py"; \
	else \
		$(VENV_PYTHON) examples/policy_check.py --run-id "$${TFE_RUN_ID}" || true; \
	fi

	@echo ""
	@echo "--- policy_evaluation.py ---"
	@if [ -z "$${TFE_TASK_STAGE_ID}" ]; then \
		echo "SKIPPED: set TFE_TASK_STAGE_ID to run policy_evaluation.py"; \
	else \
		$(VENV_PYTHON) examples/policy_evaluation.py \
			--task-stage-id "$${TFE_TASK_STAGE_ID}" || true; \
	fi

	@echo ""
	@echo "--- policy_set_parameter.py ---"
	@if [ -z "$${TFE_POLICY_SET_ID}" ]; then \
		echo "SKIPPED: set TFE_POLICY_SET_ID to run policy_set_parameter.py"; \
	else \
		$(VENV_PYTHON) examples/policy_set_parameter.py \
			--policy-set-id "$${TFE_POLICY_SET_ID}" || true; \
	fi

	@echo ""
	@echo "--- policy_set.py ---"
	-$(VENV_PYTHON) examples/policy_set.py --org "$${TFE_ORG}"

	@echo ""
	@echo "--- policy.py ---"
	@if [ -z "$${TFE_POLICY_NAME}" ]; then \
		echo "SKIPPED: set TFE_POLICY_NAME to run policy.py"; \
	else \
		$(VENV_PYTHON) examples/policy.py \
			--org "$${TFE_ORG}" \
			--policy-name "$${TFE_POLICY_NAME}" || true; \
	fi

	@echo ""
	@echo "--- project.py ---"
	-$(VENV_PYTHON) examples/project.py --list --organization "$${TFE_ORG}"

	@echo ""
	@echo "--- query_run.py ---"
	-$(VENV_PYTHON) examples/query_run.py

	@echo ""
	@echo "--- registry_module.py ---"
	-$(VENV_PYTHON) examples/registry_module.py

	@echo ""
	@echo "--- registry_provider_version.py ---"
	@if [ -z "$${TFE_REG_PROV_NS}" ] || [ -z "$${TFE_REG_PROV_NAME}" ]; then \
		echo "SKIPPED: set TFE_REG_PROV_NS and TFE_REG_PROV_NAME to run registry_provider_version.py"; \
	else \
		$(VENV_PYTHON) examples/registry_provider_version.py \
			--organization "$${TFE_ORG}" \
			--namespace "$${TFE_REG_PROV_NS}" \
			--name "$${TFE_REG_PROV_NAME}" || true; \
	fi

	@echo ""
	@echo "--- registry_provider.py ---"
	-$(VENV_PYTHON) examples/registry_provider.py

	@echo ""
	@echo "--- reserved_tag_key.py ---"
	-$(VENV_PYTHON) examples/reserved_tag_key.py

	@echo ""
	@echo "--- run_events.py ---"
	@if [ -z "$${TFE_RUN_ID}" ]; then \
		echo "SKIPPED: set TFE_RUN_ID to run run_events.py"; \
	else \
		$(VENV_PYTHON) examples/run_events.py --run-id "$${TFE_RUN_ID}" || true; \
	fi

	@echo ""
	@echo "--- run_task.py ---"
	-$(VENV_PYTHON) examples/run_task.py --org "$${TFE_ORG}"

	@echo ""
	@echo "--- run_trigger.py ---"
	-$(VENV_PYTHON) examples/run_trigger.py --org "$${TFE_ORG}"

	@echo ""
	@echo "--- run.py ---"
	-$(VENV_PYTHON) examples/run.py --organization "$${TFE_ORG}"

	@echo ""
	@echo "--- ssh_keys.py ---"
	@if [ -z "$${SSH_PRIVATE_KEY}" ]; then \
		echo "SKIPPED: set SSH_PRIVATE_KEY to run ssh_keys.py"; \
	else \
		$(VENV_PYTHON) examples/ssh_keys.py || true; \
	fi

	@echo ""
	@echo "--- state_versions.py ---"
	@if [ -z "$${TFE_WORKSPACE_ID}" ] || [ -z "$${TFE_WORKSPACE_NAME}" ]; then \
		echo "SKIPPED: set TFE_WORKSPACE_ID and TFE_WORKSPACE_NAME to run state_versions.py"; \
	else \
		$(VENV_PYTHON) examples/state_versions.py \
			--org "$${TFE_ORG}" \
			--workspace "$${TFE_WORKSPACE_NAME}" \
			--workspace-id "$${TFE_WORKSPACE_ID}" || true; \
	fi

	@echo ""
	@echo "--- variable_sets.py ---"
	-$(VENV_PYTHON) examples/variable_sets.py

	@echo ""
	@echo "--- variables.py ---"
	@if [ -z "$${TFE_WORKSPACE_ID}" ]; then \
		echo "SKIPPED: set TFE_WORKSPACE_ID to run variables.py"; \
	else \
		$(VENV_PYTHON) examples/variables.py || true; \
	fi

	@echo ""
	@echo "--- workspace_resources.py ---"
	@if [ -z "$${TFE_WORKSPACE_ID}" ]; then \
		echo "SKIPPED: set TFE_WORKSPACE_ID to run workspace_resources.py"; \
	else \
		$(VENV_PYTHON) examples/workspace_resources.py \
			--list \
			--workspace-id "$${TFE_WORKSPACE_ID}" \
			--page-size 10 || true; \
	fi

	@echo ""
	@echo "--- workspace.py ---"
	-$(VENV_PYTHON) examples/workspace.py --org "$${TFE_ORG}" --list

	@echo ""
	@echo "========================================"
	@echo "All examples completed."
	@echo "========================================"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/ dist/ $(VENV)

all: clean dev-install fmt lint test

