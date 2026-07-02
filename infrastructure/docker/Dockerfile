FROM mcr.microsoft.com/playwright:v1.50.0-jammy

LABEL maintainer="QA Team"
LABEL description="Playwright E2E Test Automation Framework with Self-Healing Agent"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    python3-venv \
    curl \
    git \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

RUN python3 -m playwright install chromium --with-deps && \
    python3 -m playwright install-deps chromium

COPY . .

RUN mkdir -p reports screenshots allure-results

RUN useradd -m -u 1001 tester && \
    chown -R tester:tester /app

USER tester

ENV HEADLESS=true
ENV BROWSER=chromium
ENV PLAYWRIGHT_TIMEOUT=30000

ENTRYPOINT ["python3", "-m", "pytest"]
CMD ["tests/", "--browser=chromium", "--headless", "--html=reports/report.html", "--self-contained-html", "-v"]
