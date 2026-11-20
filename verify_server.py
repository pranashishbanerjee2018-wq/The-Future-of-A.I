import subprocess
import time
import requests
import json
import sys
import os

os.environ["no_proxy"] = "*"
os.environ["NO_PROXY"] = "*"

def main():
    print("Testing live Flask server launch and endpoint probing with requests (no proxy)...")
    session = requests.Session()
    session.trust_env = False

    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=r"C:\Users\prana\.gemini\antigravity\scratch\future_of_ai",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2.5)

    try:
        # 1. Probe Home
        resp = session.get("http://127.0.0.1:5000/")
        print(f"HTTP GET / : {resp.status_code}")
        body = resp.text
        assert "THE FUTURE OF ARTIFICIAL INTELLIGENCE" in body
        print(f"Index HTML verified successfully ({len(body)} bytes).")

        # 2. Probe Script API
        resp = session.get("http://127.0.0.1:5000/api/script")
        print(f"HTTP GET /api/script : {resp.status_code}")
        script_data = resp.json()
        print(f"Loaded {len(script_data['scenes'])} scenes with target duration {script_data['target_duration_seconds']}s.")

        # 3. Probe Results API
        resp = session.get("http://127.0.0.1:5000/api/results")
        print(f"HTTP GET /api/results : {resp.status_code}")
        res_data = resp.json()
        print(f"Accuracy: {res_data['metrics']['accuracy_pct']}%, Precision: {res_data['metrics']['precision']}")

        # 4. Probe Decision Boundary Plot
        resp = session.get("http://127.0.0.1:5000/results/matlab_decision_boundary.png")
        print(f"HTTP GET Decision Boundary Plot : {resp.status_code} (Type: {resp.headers.get('Content-Type')})")
        assert resp.status_code == 200

        # 5. Probe Performance Metrics Plot
        resp = session.get("http://127.0.0.1:5000/results/matlab_performance_metrics.png")
        print(f"HTTP GET Performance Metrics Plot : {resp.status_code} (Type: {resp.headers.get('Content-Type')})")
        assert resp.status_code == 200

        # 6. Probe MATLAB Diagnostics API
        resp = session.get("http://127.0.0.1:5000/api/matlab/status")
        print(f"HTTP GET /api/matlab/status : {resp.status_code}")
        status_data = resp.json()
        print(f"Diagnostics: MATLAB installed = {status_data['installed']}, Cached artifacts = {status_data['has_cached_artifacts']}")

        print("\nALL SERVER LIVE ENDPOINT PROBES PASSED SUCCESSFULLY!")

    except Exception as e:
        print(f"Test Exception: {e}")
        raise

    finally:
        proc.terminate()
        out, err = proc.communicate(timeout=5)
        print("--- Flask STDOUT ---")
        print(out.decode("utf-8", errors="ignore"))
        print("--- Flask STDERR ---")
        print(err.decode("utf-8", errors="ignore"))
        print("Live Flask server process cleanly shut down.")

if __name__ == "__main__":
    main()
