tests:
	docker-compose -f docker-compose.tests.yml up test-runner
	docker-compose -f docker-compose.tests.yml down

.PHONY: build
build:
	docker-compose -f docker-compose.tests.yml build

coverage:
	docker-compose -f docker-compose.tests.yml up test-runner-coverage
	docker-compose -f docker-compose.tests.yml down

reformat:
	black --config ./black.toml .

check-format:
	black --config ./black.toml --check .

check-types:
	docker-compose -f docker-compose.tests.yml up check-types
