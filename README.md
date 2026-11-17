# RESTful Booker API Test Automation

API test automation and exploratory testing suite built with **Python**, **Pytest**, **Requests**, and **Postman** against the [RESTful Booker API](https://restful-booker.herokuapp.com/apidoc/index.html).

## Testing Strategy & Architecture

* **Risk-Based Coverage (27 Scenarios $\rightarrow$ 22 Automated Tests / 32 Pytest Executions):**
  * **Smoke Suite (`@pytest.mark.smoke` — 7 Checks):** Health check (`GET /ping`), authentication (`POST /auth`), core CRUD endpoints, and an end-to-end booking lifecycle (`POST` $\rightarrow$ `GET` $\rightarrow$ `PUT` $\rightarrow$ `GET` $\rightarrow$ `DELETE` $\rightarrow$ `GET`).
  * **Regression Suite (`@pytest.mark.regression` — 25 Executions):** Data-driven negative login tests, unauthorized access checks (`403 Forbidden` with state-preservation verification on `PUT`, `PATCH`, `DELETE`), mandatory field boundary checks, and strict JSON schema/data-type validation.
  * **Strategic CI Exclusions (5 Scenarios):** Unfixed backend bugs (inverted check-in/check-out dates and invalid calendar dates) are reproduced in Postman and documented in the defect report rather than asserted as passing or failing in CI.
* **Isolated Test Data (Zero Hardcoded IDs):** Because the public sandbox resets every 10 minutes and is shared across users, each test creates its own isolated booking via Pytest fixtures (`created_booking` in `tests/conftest.py`) right before execution.
* **Client Abstraction (`BookingClient`):** HTTP requests, headers, timeouts, and authentication methods (`Cookie` token and `Authorization: Basic`) are encapsulated in `clients/booking_client.py`.
* **Postman Suite (`postman/`):** Includes the exported Postman v2.1 collection and environment with variable chaining (`pm.environment.set`) and exploratory defect checks.

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

* [Test Plan & Scenario Matrix](docs/TEST_PLAN.md) — Mapping of all 22 automated test cases (32 executions) and 5 excluded scenarios (`TC1`–`TC27`).
* [QA Handover & Bug Report](docs/QA_handover_bug_report.md) — Reproduction steps and REST contract findings (`BUG-01` through `BUG-06`).

## Setup & Execution

1. **Clone the repository and create a virtual environment:**
   ```bash
   git clone <your-repo-url>
   cd Restful-booker-api-automation
   python -m venv .venv
   ```

2. **Activate the virtual environment:**
   * **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`
   * **macOS / Linux:** `source .venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (optional):**
   Default sandbox settings work out of the box. To override them locally, copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

5. **Run the tests:**
   * **Full suite (32 executions + HTML report):** `pytest`
   * **Smoke suite only (7 critical checks):** `pytest -m smoke`
   * **Regression suite only (25 deep checks):** `pytest -m regression`

   Open `reports/report.html` in a browser after running `pytest` to inspect test durations and results.