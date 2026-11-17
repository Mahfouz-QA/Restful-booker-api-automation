# RESTful Booker API Test Automation

![RESTFUL BOOKER Test Automation CI](https://github.com/tmpman90-tech/Restful-booker-api-automation/actions/workflows/ci.yml/badge.svg)

API test automation and exploratory testing suite built with **Python**, **Pytest**, **Requests**, and **Postman** against the [RESTful Booker API](https://restful-booker.herokuapp.com/apidoc/index.html).

## Testing Strategy & Architecture

- **Risk-Based Coverage (27 Scenarios → 22 Automated Test Cases / 32 Full-Suite Pytest Executions):**
  - **Smoke Suite (`@pytest.mark.smoke` — 7 Checks):** Health check (`GET /ping`), authentication (`POST /auth`), core CRUD endpoints, and an end-to-end booking lifecycle (`POST` → `GET` → `PUT` → `GET` → `DELETE` → `GET`).
  - **Regression Suite (`@pytest.mark.regression` — 25 Executions):** Data-driven negative login tests, unauthorized access checks (`403 Forbidden` with state-preservation verification on `PUT`, `PATCH`, `DELETE`), mandatory field boundary checks, and strict JSON schema/data-type validation.
  - **Strategic CI Exclusions (5 Scenarios):** Inverted booking dates and invalid calendar dates are documented and reproduced in Postman; date-filter boundary checks remain manual because of shared-sandbox inconsistencies; sandbox reset behavior is handled through isolated test data; and high-concurrency load testing is out of scope for the shared public sandbox.
- **CI Execution Count:** GitHub Actions runs the 7-check smoke gate first, then runs the complete 32-execution suite. The full suite includes those same 7 smoke checks, so a successful workflow performs **39 executions across both CI steps**.
- **Isolated Test Data (Zero Hardcoded IDs):** Because the public sandbox resets every 10 minutes and is shared across users, each test creates its own isolated booking via Pytest fixtures (`created_booking` in `tests/conftest.py`) right before execution.
- **Client Abstraction (`BookingClient`):** HTTP requests, headers, timeouts, and authentication methods (`Cookie` token and `Authorization: Basic`) are encapsulated in `clients/booking_client.py`.
- **Postman Suite (`postman/`):** Includes the exported Postman v2.1 collection and environment with variable chaining (`pm.environment.set`) and exploratory defect checks.

## Project Structure

```text
Restful-booker-api-automation/
├── .github/workflows/ci.yml                        # GitHub Actions CI pipeline
├── clients/booking_client.py                       # RESTful Booker API client wrapper
├── docs/
│   ├── TEST_PLAN.md                                # Risk-based test plan & scenario matrix (TC1–TC27)
│   └── QA_handover_bug_report.md                   # Defect report (BUG-01–BUG-06) & architecture notes
├── postman/
│   ├── Restful Booker.postman_collection.json      # Exported Postman v2.1 collection
│   └── Restful Booker.postman_environment.json     # Exported Postman environment variables
├── reports/                                        # Self-contained HTML reports (git-ignored)
├── tests/
│   ├── conftest.py                                 # Pytest fixtures (client, auth_token, created_booking)
│   ├── test_ping.py                                # Health check & response time test (TC1)
│   ├── test_auth.py                                # Valid & parametrized invalid auth tests (TC2–TC3)
│   └── test_bookings.py                            # CRUD, contract, E2E lifecycle & security tests (TC4–TC22)
├── utils/config.py                                 # Environment configuration loader
├── .env.example                                    # Environment variable template
├── .gitignore                                      # Ignores .venv, .idea, .env, caches & local reports
├── pytest.ini                                      # Pytest markers, discovery settings & HTML report options
└── requirements.txt                                # Pinned Python dependencies
```

## Documentation

- [Test Plan & Scenario Matrix](docs/TEST_PLAN.md) — Mapping of all 22 automated test cases (32 executions) and 5 excluded scenarios (`TC1`–`TC27`).
- [QA Handover & Bug Report](docs/QA_handover_bug_report.md) — Reproduction steps and REST contract findings (`BUG-01` through `BUG-06`).

## Setup & Execution

**Prerequisites:** Python 3.12+ and Git.

1. Clone the repository and create a virtual environment:

   ```bash
   git clone https://github.com/tmpman90-tech/Restful-booker-api-automation.git
   cd Restful-booker-api-automation
   python -m venv .venv
   ```

2. Activate the virtual environment:

   **Windows (PowerShell):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configure environment variables (optional): Default sandbox settings work out of the box. To override them locally, copy `.env.example` to `.env`:

   **Windows (PowerShell):**
   ```powershell
   Copy-Item .env.example .env
   ```

   **macOS / Linux:**
   ```bash
   cp .env.example .env
   ```

5. Run the tests:

   - Full suite (32 executions + self-contained HTML report): `pytest`
   - Smoke suite only (7 critical checks): `pytest -m smoke`
   - Regression suite only (25 executions): `pytest -m regression`

After running `pytest`, open `reports/report.html` in a browser to inspect test durations and results.
