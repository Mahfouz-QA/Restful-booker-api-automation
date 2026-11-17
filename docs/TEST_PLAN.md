# Test Plan & Risk-Based Scenario Matrix: RESTful Booker API

## 1. Document Purpose & Scope
This document defines the test strategy, risk prioritization, and scenario coverage for the RESTful Booker API automation portfolio. Rather than automating every possible input variation blindly, scenarios are evaluated by business risk, execution frequency, and API determinism to separate high-ROI automation candidates from manual/exploratory checks.

---

## 2. Naming Convention
All test cases follow a standardized, self-documenting identifier format:
`TC<Number>_<ExecutionMode>_<ResourceAndAction>_<ScenarioType>`

* **Execution Mode:** `auto` (Automated in `pytest`) | `man` (Manual / Exploratory / Excluded from CI)
* **Scenario Type:** `POS` (Positive) | `NEG` (Negative / Boundary / Security) | `CON` (Contract / Schema) | `E2E` (End-to-End Lifecycle) | `EX` (Strategic Exclusion)

---

## 3. Part A: Automated Test Suite Scope (22 Test Cases / 32 Pytest Executions)

| Test Case ID | Endpoint & Method | Scenario Objective | Suite Marker | Priority | Expected Result | Automation Rationale (QA Lead Decision) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC1_auto_ping_POS` | `GET /ping` | Verify API health check availability and response time under 2000ms | `smoke` | Critical | `201 Created` | Automate: Fast gatekeeper check; if the service is down, running the rest of the suite wastes CI time. |
| `TC2_auto_auth_valid_POS` | `POST /auth` | Generate auth token using valid admin credentials | `smoke` | Critical | `200 OK` with non-empty string `token` | Automate: Prerequisite for all protected update and delete operations across the suite. |
| `TC3_auto_auth_invalid_NEG` | `POST /auth` | Reject invalid username, invalid password, and empty payload (Parametrized x3) | `regression` | High | `200 OK` with `{"reason": "Bad credentials"}` and no `token` key | Automate: High security risk; parametrization covers 3 negative auth paths in a single reusable test function. |
| `TC4_auto_booking_create_full_POS` | `POST /booking` | Create a new booking with all required fields and optional `additionalneeds` | `smoke` | Critical | `200 OK` with integer `bookingid` and matching nested `booking` object | Automate: Core business transaction and data-creation foundation for all downstream tests. |
| `TC5_auto_booking_create_min_POS` | `POST /booking` | Create a new booking omitting the optional `additionalneeds` field | `regression` | Medium | `200 OK` with valid `bookingid` | Automate: Verifies optional field handling in the request payload contract. |
| `TC6_auto_booking_get_id_POS` | `GET /booking/{id}` | Retrieve a newly created booking by its dynamic `bookingid` | `smoke` | Critical | `200 OK` with JSON body matching all submitted booking fields | Automate: Core read verification confirming data persistence after creation. |
| `TC7_auto_booking_contract_CON` | `GET /booking/{id}` | Validate response headers, required JSON keys, and strict field data types (`str`, `int`, `bool`) | `regression` | High | `200 OK`, `Content-Type: application/json`, valid schema types | Automate: Catches silent contract-breaking changes in data types that simple status-code checks miss. |
| `TC8_auto_booking_list_all_POS` | `GET /booking` | Retrieve the list of all active booking IDs | `regression` | Medium | `200 OK` with non-empty JSON list of `{"bookingid": int}` objects | Automate: Verifies index endpoint availability and list structure. |
| `TC9_auto_booking_filter_name_POS` | `GET /booking?firstname=&lastname=` | Filter bookings by a newly created unique `firstname` and `lastname` | `regression` | Medium | `200 OK` with JSON list containing the newly created `bookingid` | Automate: High-value search feature; deterministic when using a freshly created unique name. |
| `TC10_auto_booking_put_cookie_POS` | `PUT /booking/{id}` | Full update of an existing booking using valid `Cookie: token=<token>` header | `smoke` | Critical | `200 OK` with all updated fields reflected in the response | Automate: Primary authenticated update path; critical business functionality. |
| `TC11_auto_booking_put_basic_auth_POS` | `PUT /booking/{id}` | Full update of an existing booking using valid `Authorization: Basic` header | `regression` | Medium | `200 OK` with all updated fields reflected in the response | Automate: Verifies the API's alternative authentication mechanism for protected endpoints. |
| `TC12_auto_booking_patch_POS` | `PATCH /booking/{id}` | Partial update (`firstname` and `additionalneeds` only) using valid auth token | `regression` | High | `200 OK`; target fields update while untouched fields remain unchanged | Automate: Ensures partial updates do not accidentally overwrite or null out existing fields. |
| `TC13_auto_booking_delete_POS` | `DELETE /booking/{id}` | Delete an existing booking with valid token and verify removal via `GET` | `smoke` | Critical | `DELETE` returns `201 Created`; subsequent `GET` returns `404 Not Found` | Automate: Core lifecycle completion and essential for test data cleanup. |
| `TC14_auto_booking_lifecycle_E2E` | `POST` -> `GET` -> `PUT` -> `GET` -> `DELETE` -> `GET` | End-to-end booking lifecycle from creation through modification and deletion | `smoke` | Critical | Complete chain succeeds and ends with `404 Not Found` on deleted ID | Automate: Highest business value scenario; validates state transitions across the full user journey. |
| `TC15_auto_booking_put_unauth_NEG` | `PUT /booking/{id}` | Block full update when auth token is missing or invalid (Parametrized x2) | `regression` | Critical | `403 Forbidden`; existing booking record remains unmodified | Automate: Critical access-control check preventing unauthorized data tampering. |
| `TC16_auto_booking_patch_unauth_NEG` | `PATCH /booking/{id}` | Block partial update when auth token is missing or invalid (Parametrized x2) | `regression` | High | `403 Forbidden` | Automate: Ensures partial update endpoint enforces the same security gate as full update. |
| `TC17_auto_booking_delete_unauth_NEG` | `DELETE /booking/{id}` | Block booking deletion when auth token is missing or invalid (Parametrized x2) | `regression` | Critical | `403 Forbidden`; booking remains retrievable via `GET` (`200 OK`) | Automate: Critical security check preventing unauthorized data destruction. |
| `TC18_auto_booking_get_invalid_id_NEG` | `GET /booking/{id}` | Request non-existent booking ID (`99999999`) and non-integer ID (`invalid_id`) (Parametrized x2) | `regression` | Medium | `404 Not Found` | Automate: Standard boundary and error-handling check for read operations. |
| `TC19_auto_booking_create_missing_fields_NEG` | `POST /booking` | Reject booking creation when any of the 5 mandatory fields is omitted (Parametrized x5) | `regression` | High | `500 Internal Server Error` (API defect: should be `400`, pinned to prevent crash regression) | Automate: High-ROI parametrization; 1 test function validates all 5 mandatory field rules. |
| `TC20_auto_booking_create_empty_body_NEG` | `POST /booking` | Reject empty JSON payload `{}` on booking creation | `regression` | Medium | `500 Internal Server Error` (non-200 error status; no booking created) | Automate: Verifies server rejects empty payloads without creating corrupt records. |
| `TC21_auto_booking_put_missing_field_NEG` | `PUT /booking/{id}` | Reject authenticated full update when mandatory `firstname` field is omitted | `regression` | Medium | `400 Bad Request` | Automate: Confirms update endpoint validates required schema fields. |
| `TC22_auto_booking_accept_header_NEG` | `POST /booking` | Reject booking request sent with unsupported `Accept: text/plain` header | `regression` | Low | `418 I'm a teapot` | Automate: Fast contract check verifying content-negotiation header enforcement. |

---

## 4. Part B: Strategic Exclusions & Manual / Exploratory Scope (5 Scenarios)

| Test Case ID | Endpoint & Method | Scenario Objective | Execution Mode | Strategic QA Lead Rationale (Why Excluded from Automated CI Gate) |
| :--- | :--- | :--- | :--- | :--- |
| `TC23_man_booking_inverted_dates_EX` | `POST /booking` | Submit `checkout` date earlier than `checkin` date (e.g., checkin `2026-10-10`, checkout `2026-10-01`) | Manual / Defect Log | Do Not Automate in CI Gate: The API lacks date-order validation and returns `200 OK`. Asserting `200 OK` in automation would validate a business logic bug, while asserting `400` would permanently fail CI. Logged as a known defect instead. |
| `TC24_man_booking_invalid_calendar_date_EX` | `POST /booking` | Submit impossible calendar dates (e.g., `2026-13-45`) | Manual / Defect Log | Do Not Automate in CI Gate: The API accepts impossible dates with `200 OK` and stores `"Invalid date"` strings. Documented as a data-validation defect in the QA Case Study rather than a pass/fail regression test. |
| `TC25_man_booking_filter_dates_EX` | `GET /booking?checkin=&checkout=` | Filter booking IDs using `checkin` and `checkout` query parameters | Manual / Exploratory | Do Not Automate in CI Gate: Known boundary comparison inconsistencies in the public API combined with shared sandbox data cause high flakiness and false failures. Low ROI for automated maintenance. |
| `TC26_man_sandbox_reset_persistence_EX` | Global Sandbox | Verify 10-minute automatic database reset behavior | Architectural Mitigation | Do Not Automate: Waiting 10+ minutes in a test destroys CI execution speed. Instead, we mitigate this architecturally by generating fresh dynamic test data inside every test run. |
| `TC27_man_load_stress_EX` | Global Sandbox | High-concurrency load and stress testing (`100+ req/sec`) | Out of Scope | Do Not Automate: Unethical and prohibited against a shared public practice sandbox; would degrade service availability for other users. |

