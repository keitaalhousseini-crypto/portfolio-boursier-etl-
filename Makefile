
.PHONY: test refresh load update status

test:
	.venv/bin/python -m pytest -q

refresh:
	.venv/bin/python -m scripts.refresh_yahoo_cache

load:
	.venv/bin/python -m etl.load_real

update:
	.venv/bin/python -m scripts.refresh_yahoo_cache
	.venv/bin/python -m etl.load_real

status:
	docker compose ps
