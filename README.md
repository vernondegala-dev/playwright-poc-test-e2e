# Playwright + Pytest E2E Test Automation Framework

[![Playwright](https://img.shields.io/badge/Playwright-1.61+-45ba4b?logo=playwright)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-9.0+-0A9EDC?logo=pytest)](https://docs.pytest.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-ready-326CE5?logo=kubernetes)](https://kubernetes.io)
[![Jenkins](https://img.shields.io/badge/Jenkins-pipeline-D24939?logo=jenkins)](https://jenkins.io)

A production-grade E2E test automation framework built with **Playwright**, **Pytest**, **Page Object Model**, and an AI-powered **Test QA Agent** for self-healing and automatic test generation. Learned from Udemy class.

---

## Table of Contents

- [What It Is](#what-it-is)
- [What It Can Do](#what-it-can-do)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Docker Setup](#docker-setup)
- [Kubernetes Setup](#kubernetes-setup)
- [Jenkins Pipeline](#jenkins-pipeline)
- [Test QA Agent](#test-qa-agent)
- [Configuration Reference](#configuration-reference)
- [Detailed Step-by-Step Infrastructure Guide](#detailed-step-by-step-infrastructure-guide)

---

## What It Is

This framework provides complete end-to-end test coverage for the e-commerce demo site. It tests three core flows across 26 test scenarios:

| Flow | Tests | Coverage |
|---|---|---|
| **Login** | 13 | Page load, valid/invalid auth, role selection, modal dialogs, terms, edge cases |
| **Shop** | 7 | Product listing, add to cart, cart management, navigation |
| **Checkout** | 6 | Purchase flow, country selection, terms acceptance, success verification |

Beyond testing, it ships with a **Test QA Agent** that automatically generates new test files based on page structure analysis, identifies coverage gaps, and self-heals flaky tests by finding alternative selectors when locators fail.

The entire infrastructure is codified for **Jenkins CI/CD**, **Docker**, and **Kubernetes**, making it ready for any deployment environment.

---

## What It Can Do

### Test Execution
- Run 26 E2E tests across login, shop, and checkout flows
- Filter by marker: `smoke`, `regression`, `login`, `shop`, `checkout`
- Run in parallel with `pytest-xdist` (`-n auto`)
- Auto-retry flaky tests with `pytest-rerunfailures`
- Capture screenshots + page HTML on every failure
- Generate self-contained HTML reports + JUnit XML + Allure results

### Test QA Agent
- **Auto-Generate Tests** — Scans page structure and creates test files with proper selectors
- **Coverage Gap Analysis** — Compiles existing tests against a known pattern registry and identifies what's missing
- **Self-Healing** — When a test fails due to a broken selector, the agent analyzes the page source, tries multiple strategies to find alternative selectors (text contains, aria-label, placeholder, CSS class, data attributes, XPath, nth-child), records successful healings, and can re-generate flaky test versions

### Infrastructure
- **Jenkins Pipeline** — K8s-native agent pod, multi-stage pipeline with test generation, smoke/regression runs, self-healing stage, retry re-run, Allure reporting, artifact archiving, and HTML report publishing
- **Docker** — Pre-built Playwright image with Python, Chromium, and all dependencies
- **Docker Compose** — Two-service orchestration (test runner + QA agent)
- **Kubernetes** — Full manifests: Namespace, ConfigMap, Deployment, Service, Job, RBAC, Kustomize

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Jenkins Pipeline                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │
│  │  Checkout │→│  Setup   │→│  Agent   │→│  Smoke   │→│ ... │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └─────┘ │
└─────────────────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                    ▼               ▼
           ┌────────────────┐ ┌────────────────┐
           │   Docker       │ │  Kubernetes    │
           │  Container     │ │  Pod/Job       │
           └────────────────┘ └────────────────┘
                    │               │
                    └───────┬───────┘
                            ▼
           ┌────────────────────────────────────┐
           │         Test Framework             │
           │  ┌────────┐ ┌────────┐ ┌────────┐  │
           │  │ POM    │ │ Agent  │ │ Utils  │  │
           │  │ Pages  │ │(Gen/   │ │(Config,│  │
           │  │        │ │ Heal)  │ │ Logger)│  │
           │  └────────┘ └────────┘ └────────┘  │
           └────────────────────────────────────┘
                            │
                            ▼
                ┌─────────────────────┐
                │   Target Website    │
                │ test site           │
                │   .com              │
                └─────────────────────┘
```

---

## Project Structure

```
├── src/
│   ├── pages/                    # Page Object Model (POM)
│   │   ├── login_page.py         #   Login page: auth, roles, modal
│   │   ├── shop_page.py          #   Shop page: products, add to cart
│   │   ├── cart_page.py          #   Cart page: items, remove, checkout
│   │   └── checkout_page.py      #   Checkout page: country, terms, purchase
│   ├── agent/
│   │   ├── test_generator.py     #   AI Agent: auto-generate tests, gap analysis
│   │   └── self_healer.py        #   Self-Healer: flaky test detection & remediation
│   └── utils/
│       ├── config.py             #   Centralized env-driven configuration
│       └── logger.py             #   Structured logging singleton
├── tests/
│   ├── conftest.py               # Pytest fixtures, hooks, screenshots on failure
│   ├── test_login.py             # 13 login tests (smoke + regression)
│   ├── test_shop.py              # 7 shop tests
│   ├── test_checkout.py          # 6 checkout tests
│   ├── test_agent_generated_login.py    # Auto-generated by QA Agent
│   ├── test_agent_generated_shop.py     # Auto-generated by QA Agent
│   └── test_agent_generated_checkout.py # Auto-generated by QA Agent
├── infrastructure/
│   ├── jenkins/
│   │   └── Jenkinsfile           # K8s-native declarative pipeline
│   ├── docker/
│   │   ├── Dockerfile            # Playwright + Python container
│   │   └── docker-compose.yml    # Test runner + agent services
│   └── kubernetes/
│       ├── namespace.yaml        # playwright-e2e namespace
│       ├── configmap.yaml        # Environment configuration
│       ├── deployment.yaml       # Long-running test runner + RBAC
│       ├── service.yaml          # ClusterIP service
│       ├── job.yaml              # One-shot test execution Job
│       └── kustomization.yaml    # Kustomize overlay
├── reports/                      # HTML/JUnit/Allure reports (auto-created)
├── screenshots/                  # Failure screenshots (auto-created)
├── run_agent.py                  # CLI entry point for the Test QA Agent
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── pyproject.toml                # Project metadata
├── Makefile                      # Common command shortcuts
└── README.md                     # This file
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- Git

### 1. Clone and Install
```bash
git clone <repo-url> playwright-e2e
cd playwright-e2e
pip install -r requirements.txt
python -m playwright install chromium --with-deps
```

### 2. Run All Tests
```bash
python -m pytest tests/ -v --browser=chromium --html=reports/report.html --self-contained-html
```

### 3. Run Specific Markers
```bash
# Smoke tests only (~10s)
python -m pytest tests/ -m smoke -v --browser=chromium

# Login tests only
python -m pytest tests/test_login.py -v --browser=chromium

# Regression tests
python -m pytest tests/ -m regression -v --browser=chromium
```

### 4. Run With Retries
```bash
python -m pytest tests/ --reruns=2 -v --browser=chromium
```

### 5. Run In Parallel
```bash
python -m pytest tests/ -n auto -v --browser=chromium
```

### 6. Run the Test QA Agent
```bash
# Generate new test files
python run_agent.py generate

# Analyze coverage gaps
python run_agent.py analyze

# Self-heal flaky tests
python run_agent.py heal

# All agent actions
python run_agent.py all
```

### Makefile Shortcuts
```bash
make install         # Install dependencies + Playwright browsers
make test            # Run all tests
make smoke           # Run smoke tests only
make regression      # Run regression tests only
make parallel        # Run all tests in parallel
make retry           # Run all tests with auto-retry
make agent-all       # Generate + analyze + heal
make clean           # Clean reports, screenshots, cache
```

---

## Docker Setup

### Build Image
```bash
docker build -f infrastructure/docker/Dockerfile -t playwright-e2e:latest .
```

### Run Tests via Docker
```bash
docker run --rm \
  -e HEADLESS=true \
  -e BROWSER=chromium \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/screenshots:/app/screenshots \
  playwright-e2e:latest \
  tests/ -m smoke --browser=chromium --headless -v
```

### Docker Compose (Two Services)
```bash
docker-compose -f infrastructure/docker/docker-compose.yml up --build
```

This starts two containers:
1. **playwright-tests** — Runs smoke + regression tests
2. **test-qa-agent** — Runs the QA Agent to generate tests

View reports at `./reports/` after execution.

---

## Kubernetes Setup

### Deploy All Resources
```bash
kubectl apply -k infrastructure/kubernetes/
```

This creates:
- **Namespace**: `playwright-e2e`
- **ConfigMap**: Environment variables (BASE_URL, HEADLESS, TIMEOUT, etc.)
- **Deployment**: Long-running test runner pod (1 replica)
- **Service**: ClusterIP internally exposing port 80
- **ServiceAccount + Role + RoleBinding**: RBAC for pod management

### Run Tests as a Job
```bash
kubectl apply -f infrastructure/kubernetes/job.yaml -n playwright-e2e
```

Check logs:
```bash
kubectl logs -n playwright-e2e -l app=playwright-e2e --tail=100
```

### Delete Everything
```bash
kubectl delete -k infrastructure/kubernetes/
```

---

## Jenkins Pipeline

The `Jenkinsfile` defines a complete CI/CD pipeline that runs in a Kubernetes-native agent pod:

### Pipeline Stages

| Stage | Description |
|---|---|
| **Checkout** | Clones the repository |
| **Setup Python** | Installs Python, pip deps, Playwright + Chromium |
| **Run Test Generator** | Executes the QA Agent to auto-generate test files |
| **Run Smoke Tests** | Runs `-m smoke` tests, produces JUnit + HTML + Allure |
| **Run Regression Tests** | Runs `-m regression` tests, same outputs |
| **Self-Heal Flaky Tests** | Scans heal DB, re-generates healed test variants |
| **Re-run with Retries** | Final run with `--reruns=2` on flaky tests |
| **Generate Allure Report** | Prepares Allure results for publishing |
| **Archive Artifacts** | Archives reports, screenshots, Allure results |
| **Notify** | Logs build result |

### Agent Specification
```yaml
agent:
  kubernetes:
    label "playwright-agent"
    yaml """
      containers:
        - name: playwright
          image: mcr.microsoft.com/playwright:v1.50.0-jammy
          resources:
            requests: { memory: "2Gi", cpu: "1" }
            limits:   { memory: "4Gi", cpu: "2" }
    """
```

### Plugins Required
- **Pipeline** (workflow-aggregator)
- **Kubernetes** (kubernetes)
- **HTML Publisher** (htmlpublisher)
- **JUnit** (junit)
- **Allure** (allure-jenkins-plugin) — optional

---

## Test QA Agent

The Test QA Agent is an AI-powered subsystem with two components.

### 1. Test Generator (`src/agent/test_generator.py`)

**Capabilities:**
- Maintains a registry of known test patterns (19 login, 9 shop, 7 checkout)
- Scans page source via regex to extract forms, buttons, inputs, links, dropdowns, checkboxes, radios, tables, cards
- Generates valid Python test files with proper POM imports and pytest markers
- Identifies coverage gaps by comparing generated patterns against existing tests using AST parsing
- Outputs categorized test files: `test_agent_generated_login.py`, `test_agent_generated_shop.py`, `test_agent_generated_checkout.py`

**Run:**
```bash
python run_agent.py generate
```

### 2. Self-Healer (`src/agent/self_healer.py`)

**How it works:**
1. Maintains a **heal database** (`reports/heal_db.json`) with records of every healing event
2. When a locator fails, analyzes the page source using 7 fallback strategies:
   - `text_contains` — `text=Button Label`
   - `aria_label` — `[aria-label="..."]`
   - `placeholder` — `[placeholder="..."]`
   - `css_class` — `tag.classname`
   - `data_attribute` — `[data-*="..."]`
   - `nth_child` — positional fallback
   - `xpath_contains` — `//tag[contains(text(), '...')]`
3. Records successful healings to the database
4. Detects flaky tests (records with 2+ occurrences)
5. Generates self-healed test files with retry logic and alternative selectors

**Run:**
```bash
python run_agent.py heal
```

---

## Configuration Reference

All configuration is driven by environment variables, defined in `src/utils/config.py`:

| Variable | Default              | Description |
|---|----------------------|---|
| `BASE_URL` | `https: //vvv . com` | Target site base URL |
| `TEST_USERNAME` | ``                   | Valid login username |
| `TEST_PASSWORD` | ``                   | Valid login password |
| `HEADLESS` | `true`               | Run browser in headless mode |
| `BROWSER` | `chromium`           | Browser engine (chromium/firefox/webkit) |
| `PLAYWRIGHT_TIMEOUT` | `30000`              | Default timeout in ms |
| `VIEWPORT_WIDTH` | `1280`               | Browser viewport width |
| `VIEWPORT_HEIGHT` | `720`                | Browser viewport height |
| `TEST_RETRIES` | `2`                  | Number of retry attempts for flaky tests |
| `SLOW_MO` | `0`                  | Slow motion delay in ms |
| `TEST_ENV` | `production`         | Environment label |
| `SCREENSHOT_DIR` | `screenshots`        | Failure screenshot output directory |
| `REPORT_DIR` | `reports`            | Test report output directory |

---

## Detailed Step-by-Step Infrastructure Guide

### Phase 1: Local Development Setup

#### Step 1: System Prerequisites
```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip python3-venv

# Verify
python3 --version   # Must be 3.11+
pip3 --version
git --version
```

#### Step 2: Clone and Create Virtual Environment
```bash
git clone <your-repo-url> playwright-e2e
cd playwright-e2e
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

#### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Install Playwright Browsers
```bash
python -m playwright install chromium --with-deps
```

This downloads Chromium (~130 MB) and all system-level dependencies (libc, fonts, etc.).

#### Step 5: Verify Installation
```bash
python -c "
from src.utils.config import config
from src.utils.logger import logger
from src.agent.test_generator import generator
from src.agent.self_healer import healer
print('All imports OK')
print(f'Target: {config.login_url}')
"
```

#### Step 6: Run a Quick Smoke Test
```bash
python -m pytest tests/test_login.py -m smoke -v --browser=chromium
```

Expected output: `4 passed`

#### Step 7: Run All Tests
```bash
python -m pytest tests/ -v --browser=chromium --html=reports/report.html
```

Open `reports/report.html` in a browser to view the HTML report.

---

### Phase 2: Docker Infrastructure

#### Step 1: Install Docker
```bash
# macOS: Download Docker Desktop from https://docker.com
# Ubuntu:
sudo apt-get install -y docker.io docker-compose-v2
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in
```

#### Step 2: Build the Docker Image
```bash
docker build -f infrastructure/docker/Dockerfile -t playwright-e2e:latest .
```

The Dockerfile:
- Uses `mcr.microsoft.com/playwright:v1.50.0-jammy` as base (Playwright browsers pre-installed)
- Installs Python 3.11, pip deps, and Playwright CLI
- Creates non-root `tester` user (UID 1001)
- Sets `ENTRYPOINT` to `pytest` with sensible defaults

#### Step 3: Run Tests in Container
```bash
docker run --rm \
  -e HEADLESS=true \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/screenshots:/app/screenshots \
  playwright-e2e:latest \
  tests/ --browser=chromium --headless -v
```

#### Step 4: Run QA Agent in Container
```bash
docker run --rm \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/tests:/app/tests \
  --entrypoint python3 \
  playwright-e2e:latest \
  run_agent.py all
```

#### Step 5: Use Docker Compose (Multi-Service)
```bash
docker-compose -f infrastructure/docker/docker-compose.yml up --build
```

This runs both the test suite and the QA Agent in sequence. Results populate the `./reports/` directory.

#### Step 6: Push Image to Registry (Optional)
```bash
docker tag playwright-e2e:latest ghcr.io/your-org/playwright-e2e:latest
docker push ghcr.io/your-org/playwright-e2e:latest
```

---

### Phase 3: Kubernetes Deployment

#### Step 1: Install Kubernetes Tools
```bash
# Install kubectl
# macOS:
brew install kubectl

# Ubuntu:
curl -LO "https://dl.k8s.io/release/$(curl -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Verify
kubectl version --client

# If using local K8s (Minikube, kind, or Docker Desktop K8s):
# Docker Desktop: Enable Kubernetes in Settings → Kubernetes → Enable
# Minikube: minikube start --cpus=4 --memory=8192
```

#### Step 2: Deploy All Resources
```bash
kubectl apply -k infrastructure/kubernetes/
```

This is a Kustomize overlay that applies all manifests:

1. **Namespace** (`namespace.yaml`):
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: playwright-e2e
```

2. **ConfigMap** (`configmap.yaml`):
```yaml
data:
  BASE_URL: "https:// vvvv . com"
  HEADLESS: "true"
  BROWSER: "chromium"
  PLAYWRIGHT_TIMEOUT: "30000"
  TEST_RETRIES: "2"
  TEST_ENV: "production"
```

3. **ServiceAccount + Role + RoleBinding** (in `deployment.yaml`):
```yaml
kind: ServiceAccount
metadata:
  name: playwright-sa
---
kind: Role
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
---
kind: RoleBinding
subjects:
  - kind: ServiceAccount
    name: playwright-sa
```

4. **Deployment** (`deployment.yaml`):
```yaml
kind: Deployment
metadata:
  name: playwright-e2e-runner
spec:
  replicas: 1
  template:
    spec:
      containers:
        - image: playwright-e2e:latest
          command: ["python3", "-m", "pytest", "tests/", "--browser=chromium", "--headless"]
          envFrom:
            - configMapRef:
                name: playwright-config
          resources:
            requests: { memory: "1Gi", cpu: "500m" }
            limits:   { memory: "4Gi", cpu: "2" }
      serviceAccountName: playwright-sa
```

5. **Service** (`service.yaml`): ClusterIP on port 80 (internal only)

6. **Job** (`job.yaml`): One-shot execution with `ttlSecondsAfterFinished: 86400`

#### Step 3: Verify Deployment
```bash
kubectl get all -n playwright-e2e
kubectl get pods -n playwright-e2e -w
```

#### Step 4: Run Tests as a Job
```bash
kubectl apply -f infrastructure/kubernetes/job.yaml -n playwright-e2e
```

Monitor:
```bash
kubectl get jobs -n playwright-e2e -w
kubectl logs -n playwright-e2e job/playwright-e2e-job -f
```

#### Step 5: Access Reports
```bash
# Copy reports from the pod
POD=$(kubectl get pods -n playwright-e2e -l app=playwright-e2e -o jsonpath='{.items[0].metadata.name}')
kubectl cp -n playwright-e2e $POD:/app/reports ./k8s-reports
open ./k8s-reports/report.html
```

#### Step 6: Clean Up
```bash
kubectl delete -k infrastructure/kubernetes/
```

---

### Phase 4: Jenkins CI/CD

#### Step 1: Prerequisites
- Jenkins 2.x with:
  - **Pipeline** plugin (workflow-aggregator)
  - **Kubernetes** plugin (kubernetes)
  - **HTML Publisher** plugin (htmlpublisher)
  - **JUnit** plugin (junit)
  - A configured Kubernetes cloud in Jenkins

#### Step 2: Configure Jenkins Kubernetes Cloud
1. Navigate to **Manage Jenkins → Manage Nodes and Clouds → Configure Clouds**
2. Add a new Kubernetes cloud:
   - **Name**: `kubernetes`
   - **Kubernetes URL**: Your cluster API endpoint
   - **Kubernetes Namespace**: `playwright-e2e`
   - **Pod Templates**: (leave empty — the Jenkinsfile defines it inline)

#### Step 3: Create Pipeline Job
1. **New Item → Pipeline**
2. Name: `playwright-e2e-tests`
3. **Pipeline Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `<your-repo-url>`
   - **Script Path**: `infrastructure/jenkins/Jenkinsfile`
4. **Save**

#### Step 4: Build Parameters (Optional)
Add parameters to the Jenkinsfile or job configuration:
- `BASE_URL` — Target environment URL
- `BROWSER` — Browser to test against
- `TEST_RETRIES` — Number of retries for flaky tests

#### Step 5: Run the Pipeline
Click **Build Now**. The pipeline will:
1. Spin up a K8s pod with Playwright
2. Checkout the code
3. Install dependencies
4. Run the QA Agent
5. Execute smoke → regression tests
6. Self-heal any flaky tests
7. Re-run with retries
8. Archive all reports
9. Publish HTML report

---

### Phase 5: Test QA Agent Automation

#### Step 1: Run Coverage Analysis
```bash
python run_agent.py analyze
```

Output example:
```
Test QA Agent: Analyzing test coverage...
Analysis: 26 existing tests
Missing tests (25):
  - test_add_multiple_quantities
  - test_browser_back_after_login
  - test_empty_fields
  ...
```

#### Step 2: Generate New Tests
```bash
python run_agent.py generate
```

Generates ~19 new test files in `tests/test_agent_generated_*.py`. These are properly formed Python test classes with:
- Correct imports from POM modules
- `@pytest.mark.agent_generated` markers
- Skeleton test methods using proper page objects
- Docstrings describing each test

#### Step 3: Run Agent-Generated Tests
```bash
python -m pytest tests/test_agent_generated_*.py -v --browser=chromium
```

#### Step 4: Simulate a Flaky Test Failure
The self-healer requires a heal database to work. When a test fails, the `pytest_runtest_makereport` hook in `conftest.py` captures:
- Screenshot (`screenshots/failure_*.png`)
- Page source (`screenshots/failure_*.html`)

Run the healer:
```bash
python run_agent.py heal
```

This reads `reports/heal_db.json`, checks for tests with 2+ heal records, and generates `tests/test_healed_*.py` with retry logic.

#### Step 5: Schedule Agent in Cron (Optional)
```bash
# Run QA Agent every night at 2 AM
crontab -e
0 2 * * * cd /path/to/playwright-e2e && .venv/bin/python run_agent.py all >> agent.log 2>&1
```

---

### Phase 6: Production Readiness Checklist

- [ ] All 26 base tests passing
- [ ] Docker image built and pushed to registry
- [ ] K8s manifests updated with correct image reference
- [ ] Jenkins pipeline configured and tested
- [ ] QA Agent generates tests without syntax errors
- [ ] Self-heal database initialized and tested
- [ ] Reports directory writable in all environments
- [ ] Environment variables configured per environment
- [ ] Credentials (password) injected via secrets, not hardcoded
- [ ] Test retries tuned for flakiness tolerance
- [ ] Screenshot retention policy configured
- [ ] K8s resource limits tuned for your cluster size

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `TimeoutError: waiting for navigation` | The JS redirect uses `setTimeout(2000)`. Ensure `expect_navigation` timeout is at least 15s |
| `Element is not visible` (modal) | Bootstrap modals use CSS transitions. Use `.wait_for(state="visible")` instead of `.is_visible()` |
| `Country suggestions` not appearing | Angular typeahead needs `press_sequentially()` not `fill()`. Use keystroke-by-keystroke input |
| `--browser` conflict | `pytest-playwright` already registers `--browser`. Remove custom `pytest_addoption` for it |
| `label intercepts clicks` | Use `{ force: true }` or click the `<label>` element instead of the `<input>` |
| K8s pod `CrashLoopBackOff` | Check logs: `kubectl logs -n playwright-e2e <pod-name>`. Usually resource limits or missing deps |
| Docker build slow | Layer caching — only `COPY . .` and `RUN pip install` change frequently. Keep base layers |
| `NoAllureResults` | Allure CLI not installed. Use `brew install allure` (macOS) or download from GitHub |

---

## License

This project is provided as a reference architecture for educational and professional testing purposes.
