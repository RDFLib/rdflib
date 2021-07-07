tests:
	docker compose up test-runner --exit-code-from test-runner

build:
	docker compose build

coverage:
	docker compose up test-runner-coverage --exit-code-from test-runner-coverage