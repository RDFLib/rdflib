tests:
	docker-compose -f docker-compose.tests.yml up test-runner
	docker-compose -f docker-compose.tests.yml down

build:
	docker-compose -f docker-compose.tests.yml build

coverage:
	docker-compose -f docker-compose.tests.yml up test-runner-coverage
	docker-compose -f docker-compose.tests.yml down

reformat:
	black --config ./black.toml .

check-format:
	black --config ./black.toml --check .
