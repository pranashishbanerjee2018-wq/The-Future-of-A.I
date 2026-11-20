import os
import sys
import json
import time
import socket
import threading
import subprocess
import asyncio
import urllib.request

# Ensure no proxy interferes
os.environ["no_proxy"] = "*"
os.environ["NO_PROXY"] = "*"
for k in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
    os.environ.pop(k, None)

BASE_DIR = r"C:\Users\prana\.gemini\antigravity\scratch\future_of_ai"
sys.path.insert(0, BASE_DIR)

from app import app
import websockets

def run_flask():
    app.run(host="127.0.0.1", port=5006, debug=False, use_reloader=False)

async def test_full_presentation():
    # 1. Start Flask in thread
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    time.sleep(1.5)

    # 2. Start Chrome headless
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data = os.path.join(BASE_DIR, "chrome_test_profile_full")
    cmd = [
        chrome_path,
        "--headless=new",
        "--remote-debugging-port=9223",
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
        res = opener.open("http://127.0.0.1:9223/json/list", timeout=5)
        pages = json.loads(res.read().decode())
        ws_url = pages[0]["webSocketDebuggerUrl"]
        print("Connected to Tab WebSocket:", ws_url)

        async with websockets.connect(ws_url) as ws:
            msg_id = 1
            console_logs = []
            exceptions = []
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
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    pass

            reader_task = asyncio.create_task(reader())

            await send("Page.enable")
            await send("Runtime.enable")
            await send("DOM.enable")

            print("Navigating to http://127.0.0.1:5006/...")
            await send("Page.navigate", {"url": "http://127.0.0.1:5006/"})
            await asyncio.sleep(2.5)

            async def eval_js(expr):
                res = await send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
                return res.get("result", {}).get("value")

            # TEST 1: Initial Landing Screen
            print("\n--- TEST 1: Initial Landing Screen State ---")
            init_check = await eval_js("""
            ({
                curtainVisible: !document.getElementById('title-intro-curtain').classList.contains('dismissed'),
                btnStartExists: !!document.getElementById('btn-start-presentation'),
                appInitialized: !!window.presentationApp,
                scriptLoaded: !!(window.presentationApp && window.presentationApp.scriptData),
                isPlaying: window.presentationApp ? window.presentationApp.isPlaying : false
            })
            """)
            print("Landing Screen:", init_check)
            assert init_check["curtainVisible"], "Intro curtain must be visible on landing"
            assert init_check["btnStartExists"], "Start button must exist"
            assert init_check["appInitialized"], "PresentationApp must be initialized"
            assert not init_check["isPlaying"], "Presentation must not be playing before click"

            # TEST 2: Start Presentation Button Click
            print("\n--- TEST 2: Start Presentation Click Execution ---")
            # Wait for scriptData if still loading
            for _ in range(20):
                loaded = await eval_js("!!(window.presentationApp && window.presentationApp.scriptData)")
                if loaded:
                    break
                await asyncio.sleep(0.2)

            click_res = await eval_js("""
            (function() {
                const btn = document.getElementById('btn-start-presentation');
                btn.click();
                const app = window.presentationApp;
                const hasScript = app && app.scriptData && app.scriptData.scenes;
                return {
                    curtainDismissed: document.getElementById('title-intro-curtain').classList.contains('dismissed'),
                    isPlaying: app ? app.isPlaying : false,
                    speaker: hasScript ? app.scriptData.scenes[0].dialogues[0].speaker : null,
                    subtitles: document.getElementById('subtitles-content').textContent.trim()
                };
            })()
            """)
            print("After Start Click:", click_res)
            assert click_res["curtainDismissed"], "Intro curtain must be dismissed"
            assert click_res["isPlaying"], "App must be playing"

            # TEST 3: Real-Time Character Animation & Lip-Sync Phonemes Tracking
            print("\n--- TEST 3: Character Animations & Lip-Sync Over Time ---")
            mouth_states = []
            arm_states = []
            for _ in range(8):
                await asyncio.sleep(0.3)
                sample = await eval_js("""
                ({
                    seniorMouthClass: document.getElementById('senior-mouth').getAttribute('class'),
                    juniorMouthClass: document.getElementById('junior-mouth').getAttribute('class'),
                    seniorArmClass: document.getElementById('senior-right-arm').getAttribute('class'),
                    juniorSlotClass: document.getElementById('char-junior-container').className,
                    seniorSlotClass: document.getElementById('char-senior-container').className,
                    timeCurrent: document.getElementById('time-current').textContent
                })
                """)
                mouth_states.append(sample["seniorMouthClass"])
                arm_states.append(sample["seniorArmClass"])
                print(f"  Time: {sample['timeCurrent']} | Senior Mouth: {sample['seniorMouthClass']} | Arm: {sample['seniorArmClass']} | Senior Slot: {sample['seniorSlotClass']}")

            # Verify that mouth had phoneme activity
            has_active_phonemes = any("phoneme-open" in s or "phoneme-round" in s or "phoneme-mid" in s or "phoneme-wide" in s for s in mouth_states)
            print("Observed active phoneme shapes during Senior speech:", has_active_phonemes)
            assert has_active_phonemes, "Senior mouth must animate with phoneme classes"

            # TEST 4: Pause / Resume Controls
            print("\n--- TEST 4: Pause and Resume ---")
            pause_res = await eval_js("""
            (function() {
                const btnPause = document.getElementById('ctrl-play-pause');
                btnPause.click(); // Pause
                return {
                    isPaused: window.presentationApp.isPaused,
                    icon: document.getElementById('ctrl-play-pause-icon').textContent.trim()
                };
            })()
            """)
            print("Pause State:", pause_res)
            assert pause_res["isPaused"], "Must be paused"
            assert pause_res["icon"] == "▶", "Icon must be play button"

            resume_res = await eval_js("""
            (function() {
                const btnPause = document.getElementById('ctrl-play-pause');
                btnPause.click(); // Resume
                return {
                    isPaused: window.presentationApp.isPaused,
                    icon: document.getElementById('ctrl-play-pause-icon').textContent.trim()
                };
            })()
            """)
            print("Resume State:", resume_res)
            assert not resume_res["isPaused"], "Must be resumed"
            assert resume_res["icon"] == "⏸", "Icon must be pause button"

            # TEST 5: Restart Presentation
            print("\n--- TEST 5: Restart Presentation ---")
            restart_res = await eval_js("""
            (function() {
                const btnRestart = document.getElementById('ctrl-restart');
                btnRestart.click();
                return {
                    elapsedTime: window.presentationApp.elapsedTime,
                    currentSceneIdx: window.presentationApp.currentSceneIdx,
                    currentDialogueIdx: window.presentationApp.currentDialogueIdx,
                    isPlaying: window.presentationApp.isPlaying
                };
            })()
            """)
            print("Restart State:", restart_res)
            assert restart_res["elapsedTime"] == 0, "Elapsed time reset to 0"
            assert restart_res["currentSceneIdx"] == 0, "Scene reset to 0"
            assert restart_res["isPlaying"], "Presentation still playing"

            # TEST 6: Scene Navigation to Scene 4 (MATLAB Demonstration)
            print("\n--- TEST 6: Jump to Scene 4 (MATLAB Scientific Panel) ---")
            matlab_scene_res = await eval_js("""
            (function() {
                window.presentationApp.jumpToScene(3); // Scene 4 (0-indexed: 3)
                const modal = document.getElementById('matlab-scientific-modal');
                return {
                    sceneIdx: window.presentationApp.currentSceneIdx,
                    sceneBadge: document.getElementById('scene-title-badge').textContent.trim(),
                    modalHidden: modal.classList.contains('hidden')
                };
            })()
            """)
            print("Scene 4 Jump State:", matlab_scene_res)
            assert matlab_scene_res["sceneIdx"] == 3, "Current scene is Scene 4"
            assert not matlab_scene_res["modalHidden"], "MATLAB scientific modal is visible in Scene 4"

            # TEST 7: JavaScript Errors and Exceptions check
            print("\n--- TEST 7: Verification of Zero Exceptions ---")
            print(f"Total unhandled exceptions recorded: {len(exceptions)}")
            for exc in exceptions:
                print("  Exception:", exc)
            assert len(exceptions) == 0, "There must be zero unhandled JavaScript exceptions!"

            print("\n==============================================")
            print("ALL AUTOMATED BROWSER TESTS PASSED PERFECTLY!")
            print("==============================================")

            reader_task.cancel()

    finally:
        proc.kill()

if __name__ == "__main__":
    asyncio.run(test_full_presentation())
