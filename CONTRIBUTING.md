# Contributing to NMAP Security Console

Thank you for your interest in contributing to the **NMAP Security Console**! We welcome contributions from security researchers, software engineers, DevOps practitioners, and technical writers.

Please review this document to ensure a smooth and efficient collaboration process.

---

## 📜 Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors.

- **Respect and Professionalism**: Treat all team members and community contributors with empathy and respect.
- **Ethical Focus**: This tool is designed strictly for defensive security, auditing, and research. Contributions designed to facilitate malicious attacks, unauthenticated denial-of-service, or weaponized exploits will be rejected immediately.

---

## 🛠️ Prerequisites & Development Environment

Before contributing code, ensure your workstation meets the following prerequisites:

1. **Python 3.8+**: CPython runtime installed and verified via `python --version`.
2. **Nmap 7.80+**: Installed and available in system `PATH` with Nmap Scripting Engine (`vulners.nse`).
3. **Npcap / libpcap**: Appropriate packet capture driver for your OS.
4. **Git**: Version control CLI configured with your GitHub credentials.

---

## 🚀 Repository Setup & Installation

```bash
# 1. Fork the repository on GitHub
# 2. Clone your local fork:
git clone https://github.com/<your-username>/NMAP-Security-Console.git
cd NMAP-Security-Console

# 3. Create a dedicated virtual environment:
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 4. Install dependencies:
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black
```

---

## 🌿 Git Workflow & Branch Naming

All development should occur on topic branches branched off the `main` or `dev` branch.

### Branch Naming Conventions
- `feat/<short-feature-name>` (e.g., `feat/nvd-api-key-header`)
- `fix/<bug-description>` (e.g., `fix/udp-timeout-handling`)
- `docs/<doc-update>` (e.g., `docs/update-architecture-c4`)
- `refactor/<module-name>` (e.g., `refactor/caching-engine`)

### Commit Message Conventions
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

**Allowed Types**:
- `feat`: A new feature or capability.
- `fix`: A bug or runtime error fix.
- `docs`: Documentation additions or revisions.
- `style`: Formatting, missing semicolons, whitespace adjustments.
- `refactor`: Code restructuring without modifying functional behavior.
- `perf`: Code changes that improve scan throughput or memory usage.
- `test`: Adding or updating test suites.
- `chore`: Dependency updates, build configurations, or CI changes.

---

## 🐛 Issue Reporting & Feature Requests

### Reporting Bugs
Before filing an issue, please search existing issues to avoid duplicates. When opening a bug report, provide:
1. **Clear Title**: Brief summary of the bug.
2. **Environment Details**: OS version, Python version, Nmap version.
3. **Steps to Reproduce**: Exact target format and scanning module used.
4. **Expected vs. Actual Behavior**: Stack traces, terminal logs, or screenshots.

### Feature Requests
Feature proposals should clearly articulate the problem being solved, user stories, and potential technical approaches.

---

## 📥 Pull Request (PR) Process

1. **Keep PRs Focused**: Address a single feature or bug fix per pull request.
2. **Update Tests**: Ensure any modified logic is accompanied by unit or integration tests in `tests/`.
3. **Run Linting & Formatting**:
   ```bash
   black .
   flake8 main.py
   ```
4. **Execute Test Suite**:
   ```bash
   pytest -v
   ```
5. **Update Documentation**: If your PR modifies API endpoints, configuration, or UI features, update the relevant files under `docs/` (`PRD.md`, `SRS.md`, `Architecture.md`, `Development.md`).
6. **Submit PR**: Open your PR against the `main` branch with a clear description and reference any related issue numbers (e.g., `Closes #12`).

---

## 🧪 Testing & Code Quality Standards

- **PEP 8 Compliance**: Follow standard Python conventions (4-space indentation, max 100 char lines).
- **Type Annotations**: Add type hints to all newly authored functions and methods.
- **Defensive Error Handling**: Ensure external I/O (sockets, files, APIs) is protected with try-except blocks that do not crash the FastAPI application loop.
- **Sanitization**: Never execute raw string formatting into file system paths or shell commands.

---

## 🔒 Security Vulnerability Reporting

If you discover a security vulnerability (such as an injection flaw or path traversal issue), please **DO NOT** open a public GitHub issue.

Instead, submit a confidential report directly to the security lead:
- **Email**: `yonithjamad@gmail.com`
- **Subject**: `[SECURITY VULNERABILITY] NMAP Security Console`

We will review the vulnerability and coordinate a patch within 48–72 hours.

---

## 👥 Maintainer Responsibilities & Contributor Recognition

- **Review SLA**: Maintainers aim to review all opened PRs within 5 business days.
- **Recognition**: All contributors with accepted pull requests will be credited in `README.md` and release notes.

Thank you for helping make the NMAP Security Console faster, more secure, and more powerful!
