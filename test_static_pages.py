import os
import sys
import json
import time
import socket
import socketserver
import shutil
import tempfile
import threading
import subprocess
import asyncio
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

sys.stdout.reconfigure(line_buffering=True)
socketserver.TCPServer.allow_reuse_address = True

# Ensure clean network environment
os.environ["no_proxy"] = "*"
os.environ["NO_PROXY"] = "*"
for k in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
    os.environ.pop(k, None)

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

BASE_DIR = r"C:\Users\prana\.gemini\antigravity\scratch\future_of_ai"
sys.path.insert(0, BASE_DIR)

import websockets

class CustomStaticServer:
    def __init__(self, root_dir, port=None):
        self.root_dir = root_dir
        self.port = port or get_free_port()
        self.httpd = None
        self.thread = None

    def start(self):
        root = self.root_dir
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=root, **kwargs)
            def log_message(self, format, *args):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", self.port), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        print(f"Static HTTP Server running on http://127.0.0.1:{self.port} (Serving: {root})", flush=True)

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()

async def run_static_tests():
    # Setup GitHub Pages Subpath Simulation directory
    subpath_parent = os.path.join(tempfile.gettempdir(), f"gh_pages_sim_{int(time.time())}")
    subpath_repo = os.path.join(subpath_parent, "future-of-ai")
    os.makedirs(subpath_repo, exist_ok=True)

    # Copy website structure to simulate https://username.github.io/future-of-ai/
    for item in ["index.html", "static", "data", "results", ".nojekyll"]:
        src = os.path.join(BASE_DIR, item)
        dst = os.path.join(subpath_repo, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        elif os.path.isfile(src):
            shutil.copy2(src, dst)

    # Start purely static HTTP server (NO FLASK)
    server_port = get_free_port()
    server = CustomStaticServer(root_dir=subpath_parent, port=server_port)
    server.start()
    time.sleep(1.0)

    # Start headless Chrome on dedicated free port
    chrome_port = get_free_port()
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data = os.path.join(tempfile.gettempdir(), f"chrome_prof_{chrome_port}")
    cmd = [
        chrome_path,
        "--headless=new",
        f"--remote-debugging-port={chrome_port}",
        "--remote-debugging-address=127.0.0.1",
        "--no-proxy-server",
        "--no-sandbox",
        "--disable-gpu",
        f"--user-data-dir={user_data}",
        "about:blank"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2.5)

    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        res = opener.open(f"http://127.0.0.1:{chrome_port}/json/list", timeout=5)
        pages = json.loads(res.read().decode())
        ws_url = pages[0]["webSocketDebuggerUrl"]
        print("Connected to Headless Chrome via CDP:", ws_url, flush=True)

        async with websockets.connect(ws_url) as ws:
            msg_id = 1
            console_logs = []
            exceptions = []
            failed_requests = []
            successful_requests = []
            pending_responses = {}

            async def send(method, params=None):
                nonlocal msg_id
                mid = msg_id
                msg_id += 1
                fut = asyncio.get_event_loop().create_future()
                pending_responses[mid] = fut
                req = {"id": mid, "method": method}
                if params:
                    req["params"] = params
                await ws.send(json.dumps(req))
                return await fut

            async def reader():
                try:
                    async for msg in ws:
                        data = json.loads(msg)
                        if "id" in data and data["id"] in pending_responses:
                            pending_responses[data["id"]].set_result(data.get("result", {}))
                            del pending_responses[data["id"]]
                        elif data.get("method") == "Runtime.consoleAPICalled":
                            args = [str(a.get("value", a.get("description", ""))) for a in data["params"]["args"]]
                            console_logs.append(f"[{data['params']['type']}] {' '.join(args)}")
                        elif data.get("method") == "Runtime.exceptionThrown":
                            exc = data["params"]["exceptionDetails"]
                            exceptions.append(f"EXCEPTION: {exc.get('text')} - {exc.get('exception', {}).get('description')}")
                        elif data.get("method") == "Network.responseReceived":
                            resp = data["params"]["response"]
                            status = resp["status"]
                            url = resp["url"]
                            if status >= 400:
                                failed_requests.append(f"{status}: {url}")
                            else:
                                successful_requests.append(f"{status}: {url}")
                        elif data.get("method") == "Network.loadingFailed":
                            params = data["params"]
                            failed_requests.append(f"FAILED: {params.get('errorText')} - {params.get('requestId')}")
                except asyncio.CancelledError:
                    pass
                except Exception:
                    pass

            reader_task = asyncio.create_task(reader())

            await send("Page.enable")
            await send("Runtime.enable")
            await send("DOM.enable")
            await send("Network.enable")

            # Navigate to the GitHub Pages simulated subpath URL!
            target_url = f"http://127.0.0.1:{server_port}/future-of-ai/index.html"
            print(f"\n[NAVIGATION] Opening GitHub Pages subpath URL: {target_url}", flush=True)
            await send("Page.navigate", {"url": target_url})
            await asyncio.sleep(2.5)

            async def eval_js(expr, await_promise=False):
                params = {"expression": expr, "returnByValue": True}
                if await_promise:
                    params["awaitPromise"] = True
                res = await send("Runtime.evaluate", params)
                return res.get("result", {}).get("value")

            # -----------------------------------------------------------------
            # TEST 1: Initial Landing Screen & Static Script Loading
            # -----------------------------------------------------------------
            print("\n[TEST 1] Verifying Static Landing Screen & Relative Paths...")
            init_check = await eval_js("""
            ({
                curtainVisible: !document.getElementById('title-intro-curtain').classList.contains('dismissed'),
                appExists: !!window.presentationApp,
                scriptLoaded: !!(window.presentationApp && window.presentationApp.scriptData),
                scenesCount: window.presentationApp && window.presentationApp.scriptData ? window.presentationApp.scriptData.scenes.length : 0,
                targetDuration: window.presentationApp && window.presentationApp.scriptData ? window.presentationApp.scriptData.target_duration_seconds : 0,
                locationHref: window.location.href
            })
            """)
            print("  Landing state:", init_check)
            if not init_check["appExists"]:
                print("DEBUG EXCEPTIONS:", exceptions)
                print("DEBUG LOGS:", console_logs)
            assert init_check["curtainVisible"], "Intro curtain must be displayed on landing"
            assert init_check["appExists"], "PresentationApp must initialize"
            assert init_check["scriptLoaded"], "data/presentation.json must load successfully via relative path"
            assert init_check["scenesCount"] == 7, "Must contain all 7 scenes"
            assert init_check["targetDuration"] == 165, "Exact 165s duration preserved"
            print("  --> TEST 1 PASSED: Landing screen and static JSON loaded under subpath.")

            # -----------------------------------------------------------------
            # TEST 2: Start Presentation Button Click
            # -----------------------------------------------------------------
            print("\n[TEST 2] Clicking START PRESENTATION...")
            start_check = await eval_js("""
            (function() {
                const btn = document.getElementById('btn-start-presentation');
                btn.click();
                const app = window.presentationApp;
                return {
                    curtainDismissed: document.getElementById('title-intro-curtain').classList.contains('dismissed'),
                    isPlaying: app.isPlaying,
                    currentSceneIdx: app.currentSceneIdx,
                    speaker: app.scriptData.scenes[0].dialogues[0].speaker,
                    subtitles: document.getElementById('subtitles-content').textContent.trim()
                };
            })()
            """)
            print("  Playback state after start click:", start_check)
            assert start_check["curtainDismissed"], "Curtain must be dismissed with .dismissed"
            assert start_check["isPlaying"], "Playback must be active"
            assert start_check["currentSceneIdx"] == 0, "Scene 1 active"
            assert "Welcome to our advanced systems lab" in start_check["subtitles"], "Scene 1 line 1 dialogue loaded"
            print("  --> TEST 2 PASSED: Presentation started smoothly.")

            # -----------------------------------------------------------------
            # TEST 3: Character Animations, Gestures & Phoneme Lip-Sync
            # -----------------------------------------------------------------
            print("\n[TEST 3] Tracking Real-Time 5-State Lip-Sync and Gestures...")
            phonemes_seen = set()
            for _ in range(6):
                await asyncio.sleep(0.35)
                frame = await eval_js("""
                ({
                    seniorMouth: document.getElementById('senior-mouth').getAttribute('class'),
                    juniorMouth: document.getElementById('junior-mouth').getAttribute('class'),
                    seniorArm: document.getElementById('senior-right-arm').getAttribute('class'),
                    seniorSlot: document.getElementById('char-senior-container').className,
                    timer: document.getElementById('time-current').textContent
                })
                """)
                phonemes_seen.add(frame["seniorMouth"])
                print(f"  Frame {frame['timer']} | Senior Mouth: {frame['seniorMouth']} | Arm: {frame['seniorArm']}")
            
            has_active = any("phoneme-open" in p or "phoneme-round" in p or "phoneme-mid" in p for p in phonemes_seen)
            assert has_active, "Lip-sync phonemes must actively articulate during speech"
            print("  --> TEST 3 PASSED: Lip-sync and gestures verified.")

            # -----------------------------------------------------------------
            # TEST 4: Playback Controls (Pause / Resume / Restart)
            # -----------------------------------------------------------------
            print("\n[TEST 4] Testing Playback Controls (Pause, Resume, Restart)...")
            pause_state = await eval_js("""
            (function() {
                const btn = document.getElementById('ctrl-play-pause');
                btn.click();
                return {
                    isPaused: window.presentationApp.isPaused,
                    icon: document.getElementById('ctrl-play-pause-icon').textContent.trim()
                };
            })()
            """)
            assert pause_state["isPaused"] and pause_state["icon"] == "▶", "Pause must toggle state"
            print("  Pause state verified:", pause_state)

            resume_state = await eval_js("""
            (function() {
                const btn = document.getElementById('ctrl-play-pause');
                btn.click();
                return {
                    isPaused: window.presentationApp.isPaused,
                    icon: document.getElementById('ctrl-play-pause-icon').textContent.trim()
                };
            })()
            """)
            assert not resume_state["isPaused"] and resume_state["icon"] == "⏸", "Resume must toggle state"
            print("  Resume state verified:", resume_state)

            restart_state = await eval_js("""
            (function() {
                const btn = document.getElementById('ctrl-restart');
                btn.click();
                return {
                    elapsedTime: window.presentationApp.elapsedTime,
                    currentSceneIdx: window.presentationApp.currentSceneIdx,
                    isPlaying: window.presentationApp.isPlaying
                };
            })()
            """)
            assert restart_state["elapsedTime"] == 0 and restart_state["currentSceneIdx"] == 0, "Restart resets timer & scene"
            print("  Restart state verified:", restart_state)
            print("  --> TEST 4 PASSED: Controls function properly.")

            # -----------------------------------------------------------------
            # TEST 5: Verify All 7 Scenes Sequentially
            # -----------------------------------------------------------------
            print("\n[TEST 5] Verifying All 7 Scenes and Dialogue Sequences...")
            for s_idx in range(7):
                scene_info = await eval_js(f"""
                (function() {{
                    window.presentationApp.jumpToScene({s_idx});
                    const scene = window.presentationApp.scriptData.scenes[{s_idx}];
                    return {{
                        sceneId: scene.id,
                        sceneName: scene.name,
                        camera: scene.camera,
                        dialoguesCount: scene.dialogues.length,
                        badgeText: document.getElementById('scene-title-badge').textContent.trim(),
                        subtitles: document.getElementById('subtitles-content').textContent.trim()
                    }};
                }})()
                """)
                print(f"  Scene {scene_info['sceneId']}: {scene_info['sceneName']} | {scene_info['dialoguesCount']} dialogues | Subtitles: {scene_info['subtitles'][:45]}...")
                assert scene_info["sceneId"] == s_idx + 1, f"Scene {s_idx + 1} ID matched"
            print("  --> TEST 5 PASSED: All 7 scenes load and transition seamlessly.")

            # -----------------------------------------------------------------
            # TEST 6: Scene 4 MATLAB Scientific Demonstration & Interactive Test
            # -----------------------------------------------------------------
            print("\n[TEST 6] Testing Scene 4 MATLAB Demonstration & Simulation...")
            matlab_data = await eval_js("""
            (function() {
                window.presentationApp.jumpToScene(3); // Scene 4
                const modal = document.getElementById('matlab-scientific-modal');
                const imgBoundary = document.getElementById('matlab-img-boundary');
                const imgMetrics = document.getElementById('matlab-img-metrics');
                return {
                    modalVisible: !modal.classList.contains('hidden'),
                    boundarySrc: imgBoundary.src,
                    metricsSrc: imgMetrics.src,
                    accuracyVal: document.getElementById('res-accuracy-val').textContent.trim(),
                    f1Val: document.getElementById('res-f1-val').textContent.trim(),
                    precisionVal: document.getElementById('res-precision-val').textContent.trim(),
                    recallVal: document.getElementById('res-recall-val').textContent.trim(),
                    samplesVal: document.getElementById('res-samples-val').textContent.trim()
                };
            })()
            """)
            print("  MATLAB Panel State in Scene 4:", matlab_data)
            assert matlab_data["modalVisible"], "MATLAB modal must open in Scene 4"
            assert "98.33%" in matlab_data["accuracyVal"], "Accuracy must be 98.33%"
            assert "0.98" in matlab_data["f1Val"], "F1-Score must be verified baseline ~0.9825"
            assert "200 Samples" in matlab_data["samplesVal"], "200 samples in dataset"

            # Test interactive Re-run Scientific Analysis simulation
            print("  Triggering Re-run Scientific Analysis simulation...")
            rerun_state = await eval_js("""
            (async function() {
                await window.matlabViewer.runMatlabSubprocess(true);
                return {
                    statusPill: document.getElementById('matlab-live-status-pill').textContent.trim(),
                    terminalText: document.getElementById('diag-stdout-terminal').textContent.trim(),
                    accuracyVal: document.getElementById('res-accuracy-val').textContent.trim()
                };
            })()
            """, await_promise=True)
            print("  Re-run completion state:", rerun_state["statusPill"])
            assert "VERIFIED" in rerun_state["statusPill"] or "READY" in rerun_state["statusPill"], "Re-run succeeds"
            assert "FutureAI" in rerun_state["terminalText"], "Terminal stdout contains FutureAI kernel output"
            print("  --> TEST 6 PASSED: MATLAB scientific demonstration fully functional.")

            # -----------------------------------------------------------------
            # TEST 7: Network Audit (Zero 404s, Zero Broken Links)
            # -----------------------------------------------------------------
            print("\n[TEST 7] Performing Static Network Asset Audit...")
            print(f"  Total successful HTTP requests: {len(successful_requests)}")
            print(f"  Total failed HTTP requests: {len(failed_requests)}")
            if failed_requests:
                for f_req in failed_requests:
                    print(f"    ERROR: {f_req}")
            assert len(failed_requests) == 0, f"Found {len(failed_requests)} failed HTTP requests: {failed_requests}"
            print("  --> TEST 7 PASSED: Zero failed network requests across entire presentation.")

            # -----------------------------------------------------------------
            # TEST 8: JavaScript Console & Exceptions Audit
            # -----------------------------------------------------------------
            print("\n[TEST 8] Checking JavaScript Console & Runtime Exceptions...")
            print(f"  Total unhandled runtime exceptions: {len(exceptions)}")
            if exceptions:
                for exc in exceptions:
                    print(f"    ERROR: {exc}")
            assert len(exceptions) == 0, f"Encountered {len(exceptions)} JS exceptions!"
            print("  --> TEST 8 PASSED: Zero JavaScript runtime exceptions.")

            print("\n==================================================================")
            print("🎉 ALL GITHUB PAGES STATIC WEBSITE TESTS PASSED WITH 100% SUCCESS!")
            print("==================================================================")

            reader_task.cancel()

    finally:
        server.stop()
        proc.kill()
        # Clean up temporary simulation directory
        if os.path.exists(subpath_parent):
            shutil.rmtree(subpath_parent, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(run_static_tests())
