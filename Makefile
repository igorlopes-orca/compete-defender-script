.PHONY: run tests

run:
	set -a && . ./.env && set +a && uv run defender-savings

tests:
	uv run pytest
