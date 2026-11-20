"""
THE FUTURE OF ARTIFICIAL INTELLIGENCE
MATLAB Subprocess Execution and Diagnostic Engine
File: matlab_runner.py
"""

import os
import sys
import subprocess
import shutil
import time
import json
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
MATLAB_SCRIPT = "FutureAI.m"

COMMON_MATLAB_SEARCH_PATHS = [
    # 64-bit Program Files MathWorks MATLAB versions
    r"C:\Program Files\MATLAB\R2026b\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2026a\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2025b\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2025a\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2024b\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2024a\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2023b\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2023a\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2022b\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2022a\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2021b\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2021a\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2020b\bin\matlab.exe",
    r"C:\Program Files\MATLAB\R2020a\bin\matlab.exe",
    r"C:\Program Files (x86)\MATLAB\R2024b\bin\matlab.exe",
    r"C:\Program Files (x86)\MATLAB\R2023b\bin\matlab.exe",
    r"D:\Program Files\MATLAB\R2024b\bin\matlab.exe",
    r"D:\Program Files\MATLAB\R2023b\bin\matlab.exe",
    r"D:\MATLAB\bin\matlab.exe",
    r"C:\MATLAB\bin\matlab.exe"
]

COMMON_OCTAVE_SEARCH_PATHS = [
    r"C:\Program Files\GNU Octave\*\mingw64\bin\octave-cli.exe",
    r"C:\Program Files\Octave\*\bin\octave-cli.exe",
    r"C:\Octave\*\bin\octave-cli.exe"
]


def load_config():
    """Load configurable parameters such as custom MATLAB executable path."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(cfg):
    """Save configurable parameters."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def detect_matlab_binary():
    """
    Detects installed MATLAB or Octave executable.
    Checks:
    1. Environment variable MATLAB_PATH
    2. Local config.json 'matlab_path'
    3. System PATH ('matlab.exe', 'matlab')
    4. Common Windows installation directories
    5. GNU Octave fallback ('octave-cli.exe')
    """
    # 1. Environment variable
    env_path = os.environ.get("MATLAB_PATH")
    if env_path and os.path.isfile(env_path):
        return {"path": env_path, "type": "matlab", "source": "environment_variable"}

    # 2. Config file
    cfg = load_config()
    cfg_path = cfg.get("matlab_path")
    if cfg_path and os.path.isfile(cfg_path):
        return {"path": cfg_path, "type": "matlab", "source": "config_file"}

    # 3. System PATH
    which_matlab = shutil.which("matlab") or shutil.which("matlab.exe")
    if which_matlab:
        return {"path": which_matlab, "type": "matlab", "source": "system_path"}

    # 4. Standard Windows Installation Paths
    for p in COMMON_MATLAB_SEARCH_PATHS:
        if os.path.isfile(p):
            return {"path": p, "type": "matlab", "source": "standard_program_files"}

    # Dynamic wildcard check under C:\Program Files\MATLAB
    base_pf = r"C:\Program Files\MATLAB"
    if os.path.exists(base_pf):
        for release_dir in os.listdir(base_pf):
            candidate = os.path.join(base_pf, release_dir, "bin", "matlab.exe")
            if os.path.isfile(candidate):
                return {"path": candidate, "type": "matlab", "source": f"discovered_{release_dir}"}

    # 5. GNU Octave fallback
    which_octave = shutil.which("octave-cli") or shutil.which("octave")
    if which_octave:
        return {"path": which_octave, "type": "octave", "source": "system_path"}

    for pattern in COMMON_OCTAVE_SEARCH_PATHS:
        matches = glob.glob(pattern)
        if matches:
            return {"path": matches[0], "type": "octave", "source": "standard_octave_path"}

    return None


def get_matlab_status():
    """Returns detailed diagnostics of MATLAB environment and configuration."""
    detected = detect_matlab_binary()
    cfg = load_config()
    
    # Check if results currently exist
    boundary_plot = os.path.join(RESULTS_DIR, "matlab_decision_boundary.png")
    metrics_plot = os.path.join(RESULTS_DIR, "matlab_performance_metrics.png")
    results_json = os.path.join(RESULTS_DIR, "matlab_results.json")
    results_csv = os.path.join(RESULTS_DIR, "matlab_results.csv")

    has_artifacts = (
        os.path.exists(boundary_plot) and 
        os.path.exists(metrics_plot) and 
        os.path.exists(results_json)
    )

    last_run_data = None
    if os.path.exists(results_json):
        try:
            with open(results_json, "r", encoding="utf-8") as f:
                last_run_data = json.load(f)
        except Exception:
            pass

    return {
        "installed": detected is not None,
        "details": detected if detected else {
            "message": "MATLAB Desktop executable not detected in standard system locations.",
            "searched_paths": COMMON_MATLAB_SEARCH_PATHS[:5],
            "recommendation": "Set custom path in configuration or add MATLAB bin folder to system PATH."
        },
        "configured_path": cfg.get("matlab_path", ""),
        "has_cached_artifacts": has_artifacts,
        "last_execution": last_run_data,
        "script_path": os.path.join(BASE_DIR, MATLAB_SCRIPT),
        "results_dir": RESULTS_DIR
    }


def execute_matlab_script(custom_path=None):
    """
    Executes FutureAI.m using actual installed MATLAB in batch mode.
    Captures stdout, stderr, execution time, and validates created output files.
    """
    start_time = time.time()
    
    # 1. Resolve binary
    binary_info = None
    if custom_path and os.path.isfile(custom_path):
        binary_info = {"path": custom_path, "type": "matlab", "source": "user_parameter"}
    else:
        binary_info = detect_matlab_binary()

    if not binary_info:
        return {
            "success": False,
            "error": "MATLAB executable not found. Please install MATLAB Desktop or provide its full path in the diagnostics panel.",
            "diagnostics": get_matlab_status()
        }

    matlab_exe = binary_info["path"]
    is_octave = (binary_info["type"] == "octave")

    # Record timestamps of existing files to verify fresh generation
    boundary_plot = os.path.join(RESULTS_DIR, "matlab_decision_boundary.png")
    metrics_plot = os.path.join(RESULTS_DIR, "matlab_performance_metrics.png")
    results_json = os.path.join(RESULTS_DIR, "matlab_results.json")

    # Build execution command
    # MATLAB modern versions (R2019a+) support -batch
    # MATLAB legacy versions support -nodisplay -nosplash -nodesktop -r "..."
    # Octave supports --no-gui
    cmd = []
    if is_octave:
        cmd = [matlab_exe, "--no-gui", MATLAB_SCRIPT]
    else:
        # Check if -batch flag is supported
        # We invoke -batch "FutureAI" with cwd set to BASE_DIR
        cmd = [matlab_exe, "-batch", "FutureAI"]

    print(f"[MATLAB ENGINE] Executing: {' '.join(cmd)} in {BASE_DIR}")
    
    try:
        proc = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120  # 2 minute safety timeout
        )
        elapsed_sec = round(time.time() - start_time, 2)
        stdout = proc.stdout
        stderr = proc.stderr
        return_code = proc.returncode

        # If -batch failed due to older MATLAB version, retry with legacy flags
        if return_code != 0 and "-batch" in cmd:
            legacy_cmd = [
                matlab_exe,
                "-nodisplay",
                "-nosplash",
                "-nodesktop",
                "-r",
                "try, FutureAI; catch ME, fprintf('ERROR: %s\\n', ME.message); exit(1); end; exit(0);"
            ]
            print(f"[MATLAB ENGINE] Retrying with legacy command: {' '.join(legacy_cmd)}")
            proc = subprocess.run(
                legacy_cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120
            )
            stdout += "\n" + proc.stdout
            stderr += "\n" + proc.stderr
            return_code = proc.returncode
            elapsed_sec = round(time.time() - start_time, 2)

        # File validation check
        files_created = (
            os.path.isfile(boundary_plot) and
            os.path.isfile(metrics_plot) and
            os.path.isfile(results_json)
        )

        if not files_created:
            return {
                "success": False,
                "error": "MATLAB process exited but expected output artifacts were not detected.",
                "return_code": return_code,
                "stdout": stdout,
                "stderr": stderr,
                "elapsed_seconds": elapsed_sec
            }

        # Load parsed JSON
        with open(results_json, "r", encoding="utf-8") as f:
            numerical_results = json.load(f)

        return {
            "success": True,
            "engine": "MathWorks MATLAB Desktop (Batch Execution)" if not is_octave else "GNU Octave",
            "executable": matlab_exe,
            "return_code": return_code,
            "stdout": stdout,
            "stderr": stderr,
            "elapsed_seconds": elapsed_sec,
            "results": numerical_results,
            "artifacts": {
                "decision_boundary": "/results/matlab_decision_boundary.png",
                "performance_metrics": "/results/matlab_performance_metrics.png",
                "results_json": "/results/matlab_results.json",
                "results_csv": "/results/matlab_results.csv"
            }
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "MATLAB execution timed out after 120 seconds.",
            "elapsed_seconds": round(time.time() - start_time, 2)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute MATLAB subprocess: {str(e)}",
            "elapsed_seconds": round(time.time() - start_time, 2)
        }


if __name__ == "__main__":
    print("Testing MATLAB Runner Detection...")
    status = get_matlab_status()
    print(json.dumps(status, indent=2))
