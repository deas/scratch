.PHONY: shell-fmt shell-lint shell-test

shell-fmt: ## Format shell scripts
	shfmt -i 2 -w bin/

shell-lint: ## Lint shell scripts
	shellcheck bin/*

shell-test: ## Run shell tests
	bats tests/

