.PHONY: install test smoke regression agent-generate agent-heal agent-analyze agent-all docker-build docker-run k8s-deploy k8s-delete clean

SHELL := /bin/bash

install:
	pip3 install --upgrade pip
	pip3 install -r requirements.txt
	python3 -m playwright install chromium --with-deps

test:
	python3 -m pytest tests/ -v --html=reports/report.html --self-contained-html

smoke:
	python3 -m pytest tests/ -m smoke -v --html=reports/smoke-report.html --self-contained-html

regression:
	python3 -m pytest tests/ -m regression -v --html=reports/regression-report.html --self-contained-html

parallel:
	python3 -m pytest tests/ -n auto -v --html=reports/parallel-report.html --self-contained-html

retry:
	python3 -m pytest tests/ --reruns=2 -v --html=reports/retry-report.html --self-contained-html

agent-generate:
	python3 run_agent.py generate

agent-heal:
	python3 run_agent.py heal

agent-analyze:
	python3 run_agent.py analyze

agent-all:
	python3 run_agent.py all

docker-build:
	docker build -f infrastructure/docker/Dockerfile -t playwright-e2e:latest .

docker-run:
	docker-compose -f infrastructure/docker/docker-compose.yml up --build

docker-stop:
	docker-compose -f infrastructure/docker/docker-compose.yml down

k8s-deploy:
	kubectl apply -k infrastructure/kubernetes/

k8s-delete:
	kubectl delete -k infrastructure/kubernetes/

k8s-job:
	kubectl apply -f infrastructure/kubernetes/job.yaml -n playwright-e2e

k8s-logs:
	kubectl logs -n playwright-e2e -l app=playwright-e2e --tail=100

clean:
	rm -rf reports/* screenshots/* allure-results/* .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
