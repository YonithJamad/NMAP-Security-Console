# Changelog

All notable changes to the **NMAP Security Console** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-25

### Release Summary
Initial general availability (GA) production release of the **NMAP Security Console**, featuring an asynchronous FastAPI scanning engine, glassmorphic dark-mode web user interface, real-time NIST NVD CVE correlation, and a 5-day file-backed JSON caching subsystem.

### Added
- **FastAPI Core Application**: Asynchronous REST API service (`main.py`) running on Uvicorn ASGI server.
- **Vulnerability Scanning Pipeline (`/scan/cve`)**:
  - Integration with Nmap Scripting Engine (`vulners.nse`).
  - Regex parser extracting CVE identifiers and floating-point CVSS v3 ratings.
  - Live vulnerability description enrichment via `nvdlib` querying the NIST National Vulnerability Database API 2.0.
  - Automatic CVSS severity categorization (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- **High-Speed TCP Port Scanning Engine (`/scan/tcp`)**:
  - Two-stage scanning strategy: fast 65,535 full spectrum sweep (`--min-rate 5000 -T4`) followed by targeted service version detection (`-sV`).
  - Automatic reverse DNS host resolution via `socket.gethostbyaddr`.
- **Stateless UDP Port Probing Engine (`/scan/udp`)**:
  - Full UDP port sweeping (`-sU --min-rate 1000 -T4`) with secondary version probe (`-sUV`).
- **Temporal Caching Subsystem**:
  - File-based JSON caching stored in `Pass_Scan_Data/`.
  - Automatic cache validity evaluation (`5-day TTL`).
  - Automated garbage collection routine (`perform_cleanup`) executed prior to scan dispatches.
- **Glassmorphic Presentation Suite**:
  - Central dashboard navigation hub (`index.html`).
  - Dedicated CVE Finder interface (`CVE_CVSS/CVE.html`).
  - Dedicated TCP Port Scanner interface (`TCP_Scan/TCP.html`).
  - Dedicated UDP Port Scanner interface (`UDP_Scan/UDP.html`).
  - Responsive layout, pulsing live scan indicators, and color-coded severity badges.
- **Enterprise Documentation Suite**:
  - `docs/PRD.md`: Comprehensive Product Requirements Document.
  - `docs/SRS.md`: 30-section Software Requirements Specification conforming to IEEE 830.
  - `docs/Architecture.md`: System Architecture Document with C4 and sequence diagrams.
  - `docs/UI-UX.md`: UI/UX Design System Specification.
  - `docs/Development.md`: Software Development Guide.
  - `docs/Testing.md`: Software Testing & Quality Assurance Plan.
  - `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`.

### Changed
- Refactored scanner argument arrays for maximum packet throughput while maintaining host discovery stability.
- Enhanced CORS middleware to allow flexible development and local network deployment.

### Security
- Implemented strict character whitelisting in `safe_filename()` to neutralize path traversal and arbitrary file creation attacks.
- Enforced parameterized argument handling in `python-nmap` subprocess calls to prevent command injection.
- Bound default server listening address strictly to loopback interface `127.0.0.1`.

### Known Issues
- Public NIST NVD API queries without an API key are subject to upstream rate limits (5 requests per 30 seconds), which may result in fallback descriptions during high-volume CVE lookups.

### Upcoming Changes (v1.1.0 Roadmap)
- Configuration UI for user-supplied NIST NVD API keys.
- Direct PDF and CSV executive audit report downloads.
- CIDR block subnet range scanning support.
