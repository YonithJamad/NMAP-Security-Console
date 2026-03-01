import os
import json
import re
import socket
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import nmap
import nvdlib

app = FastAPI(title="NMAP Security Console API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Pass_Scan_Data')

@app.on_event("startup")
def startup_event():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

class ScanRequest(BaseModel):
    target: str

def safe_filename(host: str, scan_type: str) -> str:
    safe_host = "".join(c for c in host if c.isalnum() or c in ('-', '.', '_'))
    return f"{scan_type.upper()}_{safe_host}.json"

def get_cached_scan(host: str, scan_type: str):
    cache_path = os.path.join(DATA_DIR, safe_filename(host, scan_type))
    
    if os.path.exists(cache_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - mtime < timedelta(days=5):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            os.remove(cache_path)
    return None

def save_scan_cache(host: str, scan_type: str, data):
    # Save scan data as JSON File
    cache_path = os.path.join(DATA_DIR, safe_filename(host, scan_type))
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
def perform_cleanup():
    # Check directory has 5 days old scan data and delete it
    try:
        now = datetime.now()
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(DATA_DIR, filename)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if now - mtime >= timedelta(days=5):
                    os.remove(filepath)
    except Exception as e:
        print(f"Error during cleanup: {e}")

# CVE CVSS Scan
def run_cve_scanner(target: str):
    try:
        nm = nmap.PortScanner()
        nm.scan(target, arguments="-F -sV --script vulners --min-rate 5000")
        
        out = nm.get_nmap_last_output()
        if isinstance(out, bytes):
            out = out.decode('utf-8', errors='ignore')
            
        pattern = r"(CVE-\d{4}-\d{4,7}).+?cvss[^\>]*\>\s*([\d\.]+)"
        matches_raw = re.findall(pattern, out, re.DOTALL)
        
        results = []
        seen = set()
        for cve_id, score_str in matches_raw:
            url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            if cve_id not in seen:
                seen.add(cve_id)
                score = float(score_str)
                if score >= 9.0:
                    level = "CRITICAL"
                elif score >= 7.0:
                    level = "HIGH"
                elif score >= 4.0:
                    level = "MEDIUM"
                else:
                    level = "LOW"
                
                desc_text = f"Vulnerability detected by Nmap vulners script. Reference: {url}"
                try:
                    nvd_res = nvdlib.searchCVE(cveId=cve_id)
                    if nvd_res and len(nvd_res) > 0:
                        desc_text = nvd_res[0].descriptions[0].value
                except Exception as e:
                    print(f"Error fetching NVD description for {cve_id}: {e}")
                
                results.append({
                    "id": cve_id,
                    "level": level,
                    "score": score,
                    "desc": desc_text
                })
                
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    except Exception as e:
        print(f"Nmap Error: {e}")
        return []

# TCP Scan
def fast_full_tcp_scan(target: str):
    nm = nmap.PortScanner()
    fast_args = '-p- -n -Pn --min-rate 5000 --max-retries 1 -T4'
    
    try:
        nm.scan(target, arguments=fast_args)
    except Exception as e:
        return [], f"Scan failed to initialize: {e}"
    
    if not nm.all_hosts():
        return [], f"No hosts found for target {target}."

    results = []
    
    for host_ip in nm.all_hosts():
        try:
            hostname = socket.gethostbyaddr(host_ip)[0]
        except Exception:
            hostname = host_ip

        if 'tcp' not in nm[host_ip] or not nm[host_ip]['tcp']:
            continue
            
        open_ports = [port for port in nm[host_ip]['tcp'] if nm[host_ip]['tcp'][port]['state'] == 'open']
        
        if not open_ports:
            continue

        port_list = ",".join(map(str, open_ports))
        version_args = f'-p {port_list} -sV -T4'
        
        try:
            nm.scan(host_ip, arguments=version_args)
        except Exception:
            pass

        if host_ip in nm.all_hosts():
            target_data = nm[host_ip]
            if 'tcp' in target_data:
                for port in sorted(target_data['tcp'].keys()):
                    p_info = target_data['tcp'][port]
                    results.append({
                        "host": host_ip,
                        "hostname": hostname,
                        "port": port,
                        "state": p_info.get('state', 'unknown'),
                        "service": p_info.get('name', 'unknown'),
                        "version": f"{p_info.get('product', '')} {p_info.get('version', '')}".strip() or "Unknown"
                    })
    
    if not results:
        return [], f"Scan completed across {len(nm.all_hosts())} hosts, but no open ports were found."
        
    return results, f"Scan completed. {len(results)} open ports found across {len(nm.all_hosts())} hosts."

# UDP Scan
def fast_full_udp_scan(target: str):
    nm = nmap.PortScanner()
    fast_args = '-sU -p- -n -Pn --min-rate 1000 --max-retries 1 -T4'
    
    try:
        nm.scan(target, arguments=fast_args)
    except Exception as e:
        return [], str(e)
    
    if not nm.all_hosts():
        return [], f"No hosts found for {target}."

    results = []
    
    for host in nm.all_hosts():
        hostname = nm[host].hostname() if nm[host].hostname() else host
        ip_address = host
        
        has_udp_data = 'udp' in nm[host]
        open_ports = []
        
        if has_udp_data:
            open_ports = [port for port in nm[host]['udp'].keys()]

        if not open_ports:
            continue

        port_list = ",".join(map(str, open_ports))
        version_args = f'-sUV -p {port_list} -T4'
        try:
            nm.scan(host, arguments=version_args)
        except Exception:
            pass

        if host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                if proto == 'udp':
                    for port in sorted(nm[host][proto].keys()):
                        p_info = nm[host][proto][port]
                        version_info = f"{p_info.get('product', '')} {p_info.get('version', '')}".strip()
                        results.append({
                            "host": ip_address,
                            "hostname": hostname,
                            "port": port,
                            "state": p_info['state'],
                            "service": p_info.get('name', 'unknown'),
                            "version": version_info or "Unknown"
                        })
                        
    if not results:
        return [], f"All scanned UDP ports on {len(nm.all_hosts())} hosts are in ignored state."
        
    return results, ""

# API Route
@app.get("/", response_class=HTMLResponse)
async def read_index():
    perform_cleanup()
    html_path = os.path.join(BASE_DIR, 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>index.html not found</h1>", status_code=404)

@app.get("/scan/cve")
async def scan_cve(host: str = Query(..., description="The target IP or Domain")):
    if not host:
        raise HTTPException(status_code=400, detail="No host provided")
        
    perform_cleanup()
    
    cached_data = get_cached_scan(host, "cve")
    if cached_data is not None:
        return cached_data

    matches = run_cve_scanner(host)
    save_scan_cache(host, "cve", matches)
    return matches

@app.get("/{module}/{filename}", response_class=HTMLResponse)
async def serve_module_html(module: str, filename: str):
    if module not in ["CVE_CVSS", "TCP_Scan", "UDP_Scan"]:
        raise HTTPException(status_code=404, detail="Module not found")
        
    file_path = os.path.join(BASE_DIR, module, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>{filename} not found in {module}</h1>", status_code=404)


@app.post("/scan/tcp")
def scan_tcp(request: ScanRequest):
    if not request.target:
        raise HTTPException(status_code=400, detail="Target is required")
        
    perform_cleanup()

    # extract data if it exists
    cached_data = get_cached_scan(request.target, "tcp")
    if cached_data is not None:
        return cached_data

    results, message = fast_full_tcp_scan(request.target)
    out_payload = {
        "ports": results,
        "message": message
    }
    save_scan_cache(request.target, "tcp", out_payload)
    return out_payload

@app.post("/scan/udp")
def scan_udp(request: ScanRequest):
    if not request.target:
        raise HTTPException(status_code=400, detail="Target is required")
        
    perform_cleanup()
        
    cached_data = get_cached_scan(request.target, "udp")
    if cached_data is not None:
        return cached_data

    results, error_msg = fast_full_udp_scan(request.target)
    out_payload = {
        "ports": results,
        "message": error_msg
    }
    save_scan_cache(request.target, "udp", out_payload)
    return out_payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
