# NMAP Security Console

A high-performance, web-based Vulnerability and Port Scanner framework powered by `python-nmap` and `FastAPI`. 
This project provides an elegant, glassmorphic UI to perform CVE (Common Vulnerabilities and Exposures) scanning, alongside deep TCP and UDP port probing, right from your browser. 

## 🚀 Features
- **Vulnerability Scan**: Detects CVEs using Nmap's `vulners` script and fetches rich descriptions from the NIST National Vulnerability Database (NVD).
- **TCP Port Scan**: Performs full 65,535 port sweeps followed by aggressive service version detection on open TCP ports.
- **UDP Port Scan**: Uncovers stateless UDP services and profiles potential attack vectors.
- **Smart Caching Engine**: Automatically caches scan results for up to 5 days, saving bandwidth and significantly speeding up repeated scans on the same target.
- **Modern UI**: Features an advanced, responsive dashboard built with Tailwind CSS.

## ⚙️ How it Works (Workflow)

1. **Frontend Initialization**: The user accesses the FastAPI server (`http://127.0.0.1:8000/`), which serves the dynamic HTML/CSS dashboard.
2. **Module Selection & Input**: The user selects a scanning module (CVE, TCP, or UDP) and submits a target IP address or Domain Name.
3. **Backend Processing & Cache Check**:
   - The FastAPI backend intercepts the request and performs an automatic cleanup of ancient cache files.
   - It checks `Pass_Scan_Data/` for valid, recent scans of the target. If found, it instantly returns the cached data.
4. **Nmap Engine Execution** (If no cache exists):
   - The backend fires up the `python-nmap` engine with specialized arguments tailored for speed and accuracy.
   - **For CVEs**, it parses the terminal output via Regex, retrieves descriptions via `nvdlib`, and scores them.
   - **For TCP/UDP**, it performs a broad sweep followed by a targeted service enumeration.
5. **Data Delivery & Rendering**: The backend saves the new scan to the cache as a JSON file, and then streams the JSON data back to the frontend, where JavaScript dynamically renders it into readable tables.

## 🛠️ Prerequisites & Installation

To run this project, make sure you have the following installed on your target machine:

### 1. Install Nmap (Required System Dependency)
The Python module requires the actual Nmap executable to function.
- **Windows**: Download and install from [Nmap.org](https://nmap.org/download.html). Ensure Nmap is added to your system's `PATH`.
- **Linux** (Debian/Ubuntu): `sudo apt install nmap`
- **macOS**: `brew install nmap`

### 2. Clone the repository
```bash
git clone https://github.com/YonithJamad/NMAP-Security-Console
cd NMAP_Project
```

### 3. Install Python Dependencies
Make sure you have Python 3.8+ installed. It is recommended to use a virtual environment. Install the required packages via pip:

```bash
pip install fastapi uvicorn python-nmap nvdlib pydantic
```

### 4. Run the Application
Start the FastAPI server utilizing Uvicorn:

```bash
python main.py
```
*(Alternatively, you can run: `uvicorn main:app --host 127.0.0.1 --port 8000 --reload`)*

### 5. Access the Dashboard
Open your web browser and navigate to:
**http://127.0.0.1:8000/**

## 📁 Directory Structure
- `main.py` - Core FastAPI backend server and Nmap scanning logic.
- `index.html` - The main landing dashboard UI.
- `CVE_CVSS/` - Frontend files for the Vulnerability Scanning module.
- `TCP_Scan/` - Frontend files for the TCP Port Scanning module.
- `UDP_Scan/` - Frontend files for the UDP Port Scanning module.
- `Pass_Scan_Data/` - Automatically generated folder where JSON cache data is stored.
