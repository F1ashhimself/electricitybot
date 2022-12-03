run:
	nohup electricitybot &

test: test-flake test-black test-isort test-unit

test-isort:
	poetry run isort --check-only -m3 .

test-black:
	poetry run black --check .

test-flake:
	poetry run flake8 .

test-unit:
	poetry run pytest --cov=src --cov-report term-missing --cov-fail-under 100

lint:
	poetry run black .
	poetry run isort .
	poetry run flake8 .
