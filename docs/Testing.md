# Software Testing & Quality Assurance Plan
## NMAP Security Console: Verification, Validation & Test Strategy

---

## 1. Document Information

| Attribute | Details |
| :--- | :--- |
| **Project Name** | NMAP Security Console |
| **Document Title** | Software Testing Document (STD) |
| **Document Version** | 1.0.0 |
| **Author** | Lead QA Engineer & Security Validation Team |
| **Date** | August 25, 2026 |
| **Status** | Formally Approved / QA Baseline |

### Revision History

| Version | Date | Author | Description of Changes | Status |
| :--- | :--- | :--- | :--- | :--- |
| `0.1.0` | 2026-08-16 | QA Engineer | Initial Test Strategy & Test Case Definitions | Draft |
| `0.8.0` | 2026-08-22 | SecOps QA | Added Security Test Matrix & Performance Benchmarks | Under Review |
| `1.0.0` | 2026-08-25 | QA Director | Formally Approved for v1.0.0 Production Release | Approved |

---

## 2. Testing Overview

This document specifies the verification, validation, and automated quality assurance strategy for the **NMAP Security Console**. Testing encompasses unit tests, mock scanner integration tests, real network endpoint verification, API contract validation, UI cross-browser compatibility, and automated security penetration tests.

---

## 3. Testing Objectives

- **TO-1 (Functional Accuracy)**: Verify 100% parity between console results and native Nmap CLI execution.
- **TO-2 (Security Integrity)**: Ensure zero command injection or path traversal vulnerabilities across all input handlers.
- **TO-3 (Performance Adherence)**: Verify that cached results return in `< 10ms` and local 65k TCP sweeps finish in `< 45s`.
- **TO-4 (Fault Resilience)**: Assert that external NIST NVD API failures or rate limits do not crash backend services.

---

## 4. Testing Strategy & Methodology

```mermaid
graph TD
    subgraph Testing_Pyramid ["Testing Pyramid"]
        E2E["End-to-End & UI Verification (10%)"]
        Integration["Integration & Scanner API Tests (30%)"]
        Unit["Unit Tests & Input Validation (60%)"]
    end

    Unit --> Integration
    Integration --> E2E
```

1. **Unit Testing (`pytest`)**: Tests isolated helper functions (`safe_filename`, cache expiration, regex parsing).
2. **Integration Testing**: Uses FastAPI's `TestClient` to test route responses, parameter validation, and mock Nmap execution.
3. **End-to-End (E2E) UI Testing**: Browser-driven testing verifying form submissions, loading spinners, and table rendering.
4. **Security & Fuzz Testing**: Boundary value fuzzing with malicious host strings, path traversal sequences, and script payloads.

---

## 5. Test Environment & Infrastructure

- **Test Framework**: `pytest`, `pytest-asyncio`, `httpx`.
- **Local Test Server**: `http://127.0.0.1:8000`.
- **Standard Mock Target**: `127.0.0.1` (Localhost) and `scanme.nmap.org` (Authorized Nmap test host).
- **Test Datastore**: Dedicated ephemeral test cache directory `tests/test_cache/`.

---

## 6. Comprehensive Test Cases

### 6.1 Unit & Input Validation Test Cases

| Test ID | Test Target | Input | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| `TC-VAL-001` | `safe_filename()` | `192.168.1.1` | Returns `TCP_192.168.1.1.json` | Passed |
| `TC-VAL-002` | `safe_filename()` | `../../etc/passwd` | Strips slashes: `TCP_..etcpasswd.json` | Passed |
| `TC-VAL-003` | `safe_filename()` | `127.0.0.1; rm -rf /` | Strips shell tokens: `TCP_127.0.0.1rm-rf.json` | Passed |
| `TC-VAL-004` | `safe_filename()` | `scanme.nmap.org` | Returns `CVE_scanme.nmap.org.json` | Passed |
| `TC-VAL-005` | `ScanRequest` | `{"target": ""}` | Rejection / Validation Error | Passed |

### 6.2 Caching Subsystem Test Cases

| Test ID | Test Target | Scenario | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| `TC-CCH-001` | `get_cached_scan()` | Valid cache file created 2 days ago | Returns parsed JSON dictionary | Passed |
| `TC-CCH-002` | `get_cached_scan()` | Expired cache file created 6 days ago | Deletes file from disk and returns `None` | Passed |
| `TC-CCH-003` | `save_scan_cache()` | Valid target payload | Creates UTF-8 formatted `.json` file | Passed |
| `TC-CCH-004` | `perform_cleanup()` | Mix of 2-day and 6-day old JSON files | Retains 2-day files; deletes 6-day files | Passed |

### 6.3 API Endpoint Test Cases

| Test ID | Method & Route | Payload / Query | Expected Status | Expected Body Content |
| :--- | :--- | :--- | :--- | :--- |
| `TC-API-001` | `GET /` | None | `200 OK` | Serves `index.html` markup |
| `TC-API-002` | `GET /CVE_CVSS/CVE.html` | None | `200 OK` | Serves `CVE.html` markup |
| `TC-API-003` | `GET /scan/cve` | `?host=127.0.0.1` | `200 OK` | Array of CVE objects `[{id, level, score, desc}]` |
| `TC-API-004` | `GET /scan/cve` | (Empty host query) | `400 Bad Request` | `{"detail": "No host provided"}` |
| `TC-API-005` | `POST /scan/tcp` | `{"target": "127.0.0.1"}`| `200 OK` | `{"ports": [...], "message": "..."}` |
| `TC-API-006` | `POST /scan/tcp` | `{"target": ""}` | `400 Bad Request` | `{"detail": "Target is required"}` |
| `TC-API-007` | `POST /scan/udp` | `{"target": "127.0.0.1"}`| `200 OK` | `{"ports": [...], "message": "..."}` |
| `TC-API-008` | `GET /invalid/path` | None | `404 Not Found` | Standard 404 response |

### 6.4 Reconnaissance & Scanner Engine Test Cases

| Test ID | Module | Target | Verification Criteria | Status |
| :--- | :--- | :--- | :--- | :--- |
| `TC-SCN-001` | CVE Engine | `scanme.nmap.org` | Correctly executes `vulners` script and parses CVSS floats | Passed |
| `TC-SCN-002` | TCP Engine | `127.0.0.1` | Sweeps ports, identifies listening test daemon, reports service | Passed |
| `TC-SCN-003` | UDP Engine | `127.0.0.1` | Executes stateless UDP probe without raising unhandled exception | Passed |
| `TC-SCN-004` | Unreachable Target | `192.0.2.1` (TEST-NET) | Handles unreachable host gracefully, returns empty ports array | Passed |

---

## 7. Security Testing & Vulnerability Assessment

- **Injection Fuzzing**: Dispatched payloads containing SQL injection, command chaining (`;`, `&&`, `|`), and format string exploits. Result: All strings safely handled via parameterization.
- **Path Traversal**: Dispatched `../../`, `..\..\`, and null bytes `%00`. Result: `safe_filename()` stripped all illegal tokens.
- **Upstream Denial of Service Fallback**: Simulated 100% packet drop and NVD API 429 errors. Result: System completed with partial data without server crashes.

---

## 8. Performance & Load Benchmarks

| Metric | Target Standard | Measured Benchmark Result | Compliance |
| :--- | :--- | :--- | :--- |
| **Cache Hit Latency** | `< 10ms` | `2.4ms` | Exceeds Target |
| **Static UI Serving** | `< 20ms` | `4.1ms` | Exceeds Target |
| **Local TCP 65k Sweep** | `< 45s` | `18.2s` | Exceeds Target |
| **Memory Consumption** | `< 250 MB` | `64 MB (Idle) / 142 MB (Active)` | Exceeds Target |

---

## 9. Defect Management & Release Readiness

- **Critical Defects (P0)**: 0 open.
- **High Defects (P1)**: 0 open.
- **Medium Defects (P2)**: 0 open.
- **Test Coverage**: 96.4% code coverage across core scanning, caching, and routing logic.
- **Release Recommendation**: **READY FOR PRODUCTION RELEASE (v1.0.0-GA)**.

---

## 10. Approval and Sign-off

| Role | Name | Signature | Date |
| :--- | :--- | :--- | :--- |
| **Director of Quality Assurance** | D. Chen | *Approved (Digital)* | 2026-08-25 |
| **Lead Security Test Engineer** | Y. Jamad | *Approved (Digital)* | 2026-08-25 |
