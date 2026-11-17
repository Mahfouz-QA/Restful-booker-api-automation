# Test Strategy & API Defect Report: RESTful Booker

## 1. Overview

This document outlines the test coverage, scope decisions, and defects identified while testing the **RESTful Booker API** (`https://restful-booker.herokuapp.com`).

Testing was organized across two complementary layers:

1. **Postman (Manual & Exploratory):** Used to map endpoints, verify `Cookie` and `Basic` authentication flows, test query parameters, and reproduce validation bugs using shared environment variables (`{{host}}`, `{{token}}`, `{{bookingid}}`).
2. **Python + Pytest + Requests (Automated CI Suite):** Covers **22 automated test cases (32 total executions with parametrization)** split into a fast **Smoke suite (7 tests)** for critical paths and a **Regression suite (25 executions)** for negative inputs, access control, and response schema checks.

---

## 2. Scope Decisions & Exclusions (`TC14`, `TC23`–`TC27`)

Not every test scenario belongs in an automated CI pipeline, and duplicating identical workflows across tools adds maintenance overhead without adding coverage. The table below explains how edge cases, environment constraints, and cross-tool overlaps were handled.

| Scenario ID | Scenario | Pytest | Postman | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **`TC14_auto_booking_lifecycle_E2E`** | Full CRUD Lifecycle (`POST` $\to$ `GET` $\to$ `PUT` $\to$ `GET` $\to$ `DELETE` $\to$ `GET`) | **Included** (Standalone test) | **Covered by Collection Run** | In Pytest, each test runs in isolation with its own fixture-created record, so `TC14` chains all 6 state transitions in one function. In Postman, adding a separate `TC14` request would be redundant because running the collection in sequence (`TC4` Create $\to$ `TC6` Get $\to$ `TC10` Put $\to$ `TC13` Delete + follow-up `GET` 404 check) already executes that exact flow using shared environment variables. |
| **`TC23_man_booking_inverted_dates_EX`** | `checkout` earlier than `checkin` (`2026-10-10` to `2026-10-01`) | **Excluded** from CI | **Included** (Manual Bug Check) | The API lacks date-order validation and returns `200 OK`. Asserting `200 OK` in CI validates broken business logic, while asserting `400` would fail every build. Logged as **BUG-02**. |
| **`TC24_man_booking_invalid_calendar_date_EX`** | Impossible calendar dates (`2026-13-45`) | **Excluded** from CI | **Included** (Manual Bug Check) | The API accepts out-of-range dates with `200 OK` and stores `"Invalid date"` strings. Kept as a manual reproduction in Postman and logged as **BUG-03**. |
| **`TC25_man_booking_filter_dates_EX`** | Filter bookings via `?checkin=&checkout=` | **Excluded** from CI | **Included** (Manual Check) | Boundary comparison inconsistencies (`>` vs `>=`) and shared sandbox records cause intermittent false failures. Logged as **BUG-06**. |
| **`TC26_man_sandbox_reset_persistence_EX`** | 10-minute automatic database reset on public host | **Excluded** (Handled by Design) | **Not Included** (No Endpoint) | There is no `/reset` endpoint to call—the 10-minute wipe is an automatic background job on the public demo server. Adding a 10+ minute wait would stall CI and break repeatable Postman runs. Instead, the suite avoids hardcoded IDs (such as `/booking/1`) and generates fresh tokens and bookings dynamically on every run. |
| **`TC27_man_load_stress_EX`** | High-concurrency load & stress testing (`100+ req/sec`) | **Out of Scope** | **Out of Scope** | Running load or stress tests (via concurrent scripts or Postman Performance Runner) against a shared public sandbox degrades service availability for other users. |

---

## 3. API Defect & HTTP Discrepancy Report

Testing in Postman and Pytest uncovered **6 functional defects and HTTP standard discrepancies**. Known HTTP quirks are asserted in the automated suite so CI stays green while catching regressions, whereas missing input validation bugs are documented below.

### BUG-01: `POST /booking` Returns Unhandled `500 Internal Server Error` When Mandatory Fields Are Omitted

* **Severity:** High | **Priority:** High
* **Endpoint:** `POST /booking`
* **Test Cases:** `TC19_auto_booking_create_missing_fields_NEG` (Parametrized x5), `TC20_auto_booking_create_empty_body_NEG`
* **Steps to Reproduce:**
  1. Send `POST {{host}}/booking` with headers `Content-Type: application/json` and `Accept: application/json`.
  2. Omit any required field (`firstname`, `lastname`, `totalprice`, `depositpaid`, or `bookingdates`), or send an empty JSON body `{}`.
* **Expected Result:** `400 Bad Request` (or `422 Unprocessable Entity`) with a JSON error message identifying the missing field.
* **Actual Result:** `500 Internal Server Error` with plain-text body `Internal Server Error`.
* **Notes:** `PUT /booking/{id}` (`TC21_auto_booking_put_missing_field_NEG`) properly validates missing required fields and returns `400 Bad Request`. Only `POST /booking` lacks pre-persistence validation, resulting in an unhandled server exception. `TC19` and `TC20` pin the `500` status in CI to verify the server rejects incomplete payloads without creating partial records.

---

### BUG-02: Inverted Booking Dates (`checkout` Before `checkin`) Accepted with `200 OK`

* **Severity:** High | **Priority:** Medium
* **Endpoints:** `POST /booking`, `PUT /booking/{id}`
* **Test Case:** `TC23_man_booking_inverted_dates_EX`
* **Steps to Reproduce:**
  1. Send `POST {{host}}/booking` with `"checkin": "2026-10-10"` and `"checkout": "2026-10-01"`.
* **Expected Result:** `400 Bad Request` rejecting a check-out date earlier than the check-in date.
* **Actual Result:** `200 OK`; the booking is created and saved with a negative stay duration (`-9` days).
* **Automation Handling:** Excluded from CI assertions (`TC23`) to avoid passing broken business logic; reproduced in Postman.

---

### BUG-03: Impossible Calendar Dates Accepted and Stored as `"Invalid date"`

* **Severity:** Medium | **Priority:** Medium
* **Endpoint:** `POST /booking`
* **Test Case:** `TC24_man_booking_invalid_calendar_date_EX`
* **Steps to Reproduce:**
  1. Send `POST {{host}}/booking` with `"checkin": "2026-13-45"` and `"checkout": "2026-14-99"`.
  2. Retrieve the created booking via `GET {{host}}/booking/{{bookingid}}`.
* **Expected Result:** `400 Bad Request` rejecting non-existent calendar dates.
* **Actual Result:** `200 OK`; date parsing fails silently and stores `"Invalid date"` (or `"0NaN-aN-aN"`) in place of valid ISO-8601 dates.
* **Automation Handling:** Excluded from CI assertions (`TC24`); reproduced in Postman.

---

### BUG-04: Failed Login Returns `200 OK` Instead of `401 Unauthorized`

* **Severity:** Low | **Priority:** Low
* **Endpoint:** `POST /auth`
* **Test Case:** `TC3_auto_auth_invalid_NEG` (Parametrized x3)
* **Steps to Reproduce:**
  1. Send `POST {{host}}/auth` with invalid credentials (`{"username": "admin", "password": "wrong_password"}`) or an empty payload `{}`.
* **Expected Result:** `401 Unauthorized`.
* **Actual Result:** `200 OK` with JSON body `{"reason": "Bad credentials"}`.
* **Automation Handling:** `TC3` checks both `data.get("reason") == "Bad credentials"` and `"token" not in data` to confirm no token is returned alongside the `200` status.

---

### BUG-05: Non-Standard `201 Created` Status Codes on `GET /ping` and `DELETE /booking/{id}`

* **Severity:** Low | **Priority:** Low
* **Endpoints:** `GET /ping`, `DELETE /booking/{id}`
* **Test Cases:** `TC1_auto_ping_POS`, `TC13_auto_booking_delete_POS`
* **Actual Behavior:** Both endpoints return `201 Created` instead of `200 OK` (health check) or `204 No Content` / `200 OK` (resource deletion).
* **Automation Handling:** Because a `201` status alone does not confirm database removal, `TC13` follows `DELETE` with a `GET /booking/{id}` request asserting `404 Not Found`.

---

### BUG-06: Date-Range Query Filter Boundary Inconsistencies

* **Severity:** Low | **Priority:** Low
* **Endpoint:** `GET /booking?checkin=YYYY-MM-DD&checkout=YYYY-MM-DD`
* **Test Case:** `TC25_man_booking_filter_dates_EX`
* **Actual Behavior:** Filtering by `checkin` and `checkout` query parameters shows inconsistent boundary matching (exclusive `>` vs. inclusive `>=`) and UTC date shifts, causing exact-match queries to intermittently omit valid bookings.
* **Automation Handling:** Kept as a manual check in Postman (`TC25`) rather than a CI assertion.

---

## 4. Test Summary & Release Assessment

| Area | Coverage & Results | Status |
| :--- | :--- | :--- |
| **Core CRUD & E2E Flow** | `POST`, `GET` (by ID, list, name filter), `PUT`, `PATCH`, and `DELETE` verified across Postman and Pytest (`TC4`–`TC14`). | **PASS** |
| **Auth & Access Control** | Token generation (`TC2`), invalid login rejection without token leakage (`TC3`), `Cookie` and `Basic` auth (`TC10`, `TC11`), and `403 Forbidden` enforcement on unauthenticated `PUT`/`PATCH`/`DELETE` (`TC15`–`TC17`). | **PASS** |
| **Schema & Content Negotiation** | Response field data types (`str`, `int`, `bool`, `dict`) validated (`TC7`), along with unsupported `Accept` header rejection (`418 I'm a teapot` in `TC22`). | **PASS** |
| **Input & Date Validation** | Unhandled `500` error on `POST` missing fields (`BUG-01`) and missing chronological/calendar date checks (`BUG-02`, `BUG-03`) documented with reproduction steps. | **CONDITIONAL (Defects Logged)** |
| **CI Automation Stability** | **32/32 Pytest runs passing** (~28s full suite; <8s smoke suite) using dynamic test data with zero hardcoded IDs (`TC26`). | **READY FOR CI** |