.PHONY: check test validate

check: test validate

test:
	PYTHONPATH=src python -m pytest -q

validate:
	PYTHONPATH=src python -m bloom_plant_library validate
