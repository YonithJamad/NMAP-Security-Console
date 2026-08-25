# Software Development Guide & Architecture Manual
## NMAP Security Console: Engineering Standards, Code Organization & Workflow

---

## 1. Document Information

| Attribute | Details |
| :--- | :--- |
| **Project Name** | NMAP Security Console |
| **Document Title** | Software Development Guide (SDG) |
| **Document Version** | 1.0.0 |
| **Author** | Core Engineering Team & Backend Architects |
| **Date** | August 25, 2026 |
| **Status** | Approved / Engineering Baseline |

### Revision History

| Version | Date | Author | Description of Changes | Status |
| :--- | :--- | :--- | :--- | :--- |
| `0.1.0` | 2026-08-15 | Lead Developer | Initial Setup, Dependency & Code Guidelines | Draft |
| `0.7.0` | 2026-08-20 | Backend Team | Added Nmap Wrappers, Caching, and Async Patterns | Under Review |
| `1.0.0` | 2026-08-25 | Principal Architect | Baselined for Production Engineering | Approved |

---

## 2. Development Overview

The **NMAP Security Console** is an asynchronous Python service built on `FastAPI` and `uvicorn`, interfacing directly with the native C/C++ `nmap` engine and the `nvdlib` threat intelligence client. This document establishes mandatory coding standards, project structures, development environments, and debugging workflows.

---

## 3. Technology Stack & Prerequisites

### 3.1 Core Technologies
- **Python**: Version 3.8 to 3.12 (CPython runtime).
- **Web Framework**: FastAPI `>= 0.100.0`.
- **ASGI Server**: Uvicorn `[standard] >= 0.22.0`.
- **Validation**: Pydantic `>= 2.0.0`.
- **Port Scanner Driver**: `python-nmap >= 0.7.1`.
- **Threat Intelligence Client**: `nvdlib >= 0.7.6`.
- **System Binary**: Nmap `>= 7.80` with Nmap Scripting Engine (`vulners.nse`).

### 3.2 System Requirements
- **OS**: Windows 10/11, Ubuntu 20.04/22.04 LTS, Debian 11/12, macOS 13+.
- **Packet Capture Driver**: Npcap (Windows) or libpcap (Linux/macOS).

---

## 4. Repository Structure & Source Code Organization

```
NMAP/
├── .gitignore               # Git exclusions (venv, __pycache__, cache JSONs)
├── README.md                # Primary user guide and project documentation
├── CHANGELOG.md             # Version release history
├── CONTRIBUTING.md          # Open-source contribution standards
├── requirements.txt         # Pinned Python package dependencies
├── main.py                  # Core FastAPI backend, routing & scanning logic
├── index.html               # Main dashboard navigation hub UI
├── CVE_CVSS/
│   └── CVE.html             # Vulnerability scanner frontend interface
├── TCP_Scan/
│   └── TCP.html             # TCP 65k port sweep frontend interface
├── UDP_Scan/
│   └── UDP.html             # UDP stateless port probe frontend interface
├── Pass_Scan_Data/          # Auto-generated directory storing 5-day JSON cache
└── docs/                    # Complete architectural and technical documentation
    ├── PRD.md               # Product Requirements Document
    ├── SRS.md               # Software Requirements Specification
    ├── Architecture.md      # System Architecture Document
    ├── UI-UX.md             # UI/UX Design System Specification
    ├── Development.md       # Software Development Guide (This file)
    └── Testing.md           # Software Testing & QA Specification
```

---

## 5. Development Environment Setup

### 5.1 Local Virtual Environment Installation

```bash
# Clone the repository
git clone https://github.com/YonithJamad/NMAP-Security-Console.git
cd NMAP-Security-Console

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.2 Nmap System Dependency Setup
- **Windows**: Download installer from `https://nmap.org/download.html`. Check "Install Npcap" during setup. Ensure `C:\Program Files (x86)\Nmap` is in system `PATH`.
- **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install -y nmap`
- **macOS**: `brew install nmap`

---

## 6. Coding Standards & Conventions

### 6.1 Python Coding Standards (PEP 8)
- **Formatting**: 4 spaces per indentation level. Maximum line length: 100 characters.
- **Type Annotations**: Explicit type hints on all function signatures (`def get_cached_scan(host: str, scan_type: str) -> Optional[dict]:`).
- **Imports**: Group imports in order: Standard Library, Third-party packages, Local modules.
- **Docstrings**: Google-style docstrings for non-trivial helper routines.

### 6.2 Frontend Standards
- **Vanilla ES6+**: Use standard `fetch()`, `async/await`, and DOM selectors (`document.getElementById`).
- **Semantic HTML5**: Ensure proper element tags (`<header>`, `<main>`, `<table>`, `<thead>`, `<tbody>`).
- **CSS**: Pure Tailwind utility classes complemented by well-scoped `.glass-panel` and `.glass-card` styling rules.

---

## 7. Git Workflow & Branching Strategy

```
main (Production Release)
  └── dev (Integration Branch)
        ├── feature/cve-api-enhancement
        ├── fix/nmap-timeout-handling
        └── refactor/cache-engine
```

- **Branch Naming**:
  - `feature/<short-description>`: New capabilities.
  - `fix/<issue-description>`: Bug and error fixes.
  - `refactor/<target-area>`: Code cleanup without functional change.
- **Commit Message Format**: Conventional Commits standard:
  - `feat(api): add export scan results endpoint`
  - `fix(scanner): prevent regex failure on multi-line banner`
  - `docs(srs): update requirement traceability matrix`

---

## 8. Backend Implementation Details (`main.py`)

### 8.1 Input Sanitization & Path Guard
```python
def safe_filename(host: str, scan_type: str) -> str:
    """Strips all illegal characters to prevent path traversal."""
    safe_host = "".join(c for c in host if c.isalnum() or c in ('-', '.', '_'))
    return f"{scan_type.upper()}_{safe_host}.json"
```

### 8.2 Caching Engine Logic
- **Lookup**: Compares `datetime.now() - mtime < timedelta(days=5)`.
- **Storage**: Dumps JSON data using `json.dump(data, f, indent=4)`.
- **Cleanup**: Iterates `Pass_Scan_Data/` and removes files older than 5 days.

### 8.3 CVE Scanner Implementation
```python
def run_cve_scanner(target: str):
    nm = nmap.PortScanner()
    nm.scan(target, arguments="-F -sV --script vulners --min-rate 5000")
    out = nm.get_nmap_last_output()
    if isinstance(out, bytes):
        out = out.decode('utf-8', errors='ignore')
        
    pattern = r"(CVE-\d{4}-\d{4,7}).+?cvss[^\>]*\>\s*([\d\.]+)"
    matches_raw = re.findall(pattern, out, re.DOTALL)
    # Deduplicate, query NIST NVD via nvdlib, and score
```

### 8.4 TCP Full Sweep Scanner Implementation
```python
def fast_full_tcp_scan(target: str):
    nm = nmap.PortScanner()
    # Stage 1: Full port sweep
    fast_args = '-p- -n -Pn --min-rate 5000 --max-retries 1 -T4'
    nm.scan(target, arguments=fast_args)
    
    # Stage 2: Targeted version sweep on discovered open ports
    # Version probe: -p <ports> -sV -T4
```

### 8.5 UDP Probing Implementation
```python
def fast_full_udp_scan(target: str):
    nm = nmap.PortScanner()
    fast_args = '-sU -p- -n -Pn --min-rate 1000 --max-retries 1 -T4'
    nm.scan(target, arguments=fast_args)
    # Version probe: -sUV -p <ports> -T4
```

---

## 9. Development Server & Execution

```bash
# Direct Python startup:
python main.py

# Or via Uvicorn CLI with hot-reload enabled:
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

- Web UI: `http://127.0.0.1:8000/`
- Interactive OpenAPI / Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc Documentation: `http://127.0.0.1:8000/redoc`

---

## 10. Error Handling & Debugging

- **Nmap Execution Errors**: Wrapped in try-except blocks, logging raw errors without terminating the API process.
- **NVD API Throttling**: If `nvdlib` raises exceptions (e.g., HTTP 429), the scanner falls back to default NSE reference strings.
- **Client Disconnection**: Uvicorn handles disconnected client sockets cleanly.

---

## 11. Security Implementation Best Practices

1. **Never use `shell=True`**: All subprocess calls are managed through `python-nmap`'s argument array parsing.
2. **Strict Ingress Filtering**: Character whitelisting in `safe_filename()` neutralizes path traversal.
3. **Localhost Binding**: Default development server binds strictly to `127.0.0.1`.

---

## 12. Approval and Sign-off

| Role | Name | Signature | Date |
| :--- | :--- | :--- | :--- |
| **Lead Backend Engineer** | Y. Jamad | *Approved (Digital)* | 2026-08-25 |
| **Principal Software Architect** | T. Albright | *Approved (Digital)* | 2026-08-25 |
