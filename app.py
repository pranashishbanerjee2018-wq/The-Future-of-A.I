"""
THE FUTURE OF ARTIFICIAL INTELLIGENCE: A Journey Through Innovation, Intelligence and Technology
Flask Backend Application Service
File: app.py
"""

import os
import json
from flask import Flask, render_template, send_from_directory, jsonify, request
from matlab_runner import get_matlab_status, execute_matlab_script, load_config, save_config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(
    __name__,
    static_folder=STATIC_DIR,
    template_folder=TEMPLATES_DIR
)

# Presentation Master Script & Timed Sequence
PRESENTATION_DATA = {
    "title": "THE FUTURE OF ARTIFICIAL INTELLIGENCE",
    "subtitle": "A Journey Through Innovation, Intelligence and Technology",
    "target_duration_seconds": 165,  # 2 minutes 45 seconds (Target: 2m 30s - 2m 50s)
    "characters": {
        "senior": {
            "id": "senior",
            "name": "Dr. Alexander Thorne",
            "role": "Senior AI Researcher",
            "age": 30,
            "attire": "Dark navy professional laboratory coat",
            "voice_profile": {"pitch": 0.88, "rate": 0.95, "gender": "male"}
        },
        "junior": {
            "id": "junior",
            "name": "Marcus Vance",
            "role": "Junior AI Researcher",
            "age": 23,
            "attire": "Smart casual blue shirt & digital tablet",
            "voice_profile": {"pitch": 1.12, "rate": 1.05, "gender": "male"}
        }
    },
    "scenes": [
        {
            "id": 1,
            "name": "The AI Research Lab",
            "camera": "cam-zoom-in",
            "active_hud": "general",
            "dialogues": [
                {
                    "speaker": "senior",
                    "text": "Welcome to our advanced systems lab. Artificial Intelligence has transitioned from theoretical speculation into the defining technology of the twenty-first century, actively transforming how humanity computes, discovers, and reasons.",
                    "expression": "confident",
                    "gesture": "welcome",
                    "duration": 12.5
                },
                {
                    "speaker": "junior",
                    "text": "The pace of deployment is staggering, Alexander. Systems that were computational benchmarks just five years ago are now everyday commodities.",
                    "expression": "analytical",
                    "gesture": "point-tablet",
                    "duration": 8.5
                }
            ]
        },
        {
            "id": 2,
            "name": "The Evolution of AI",
            "camera": "cam-neural-focus",
            "active_hud": "neural",
            "dialogues": [
                {
                    "speaker": "junior",
                    "text": "Looking at this architectural evolution, how did we shift from rigid expert systems to models that demonstrate emergent reasoning?",
                    "expression": "curious",
                    "gesture": "inquire",
                    "duration": 8.0
                },
                {
                    "speaker": "senior",
                    "text": "The breakthrough emerged when we replaced hard-coded symbolic logic with statistical optimization. By training deep neural networks across massive data topologies, machines learn hierarchical representations rather than following brittle rules.",
                    "expression": "explaining",
                    "gesture": "present-screen",
                    "duration": 13.5
                }
            ]
        },
        {
            "id": 3,
            "name": "AI in the Real World",
            "camera": "cam-two-shot",
            "active_hud": "real-world",
            "dialogues": [
                {
                    "speaker": "junior",
                    "text": "And the empirical impact is evident everywhere—accelerating oncology diagnosis in healthcare, optimizing autonomous transportation, and automating robotic synthesis.",
                    "expression": "enthusiastic",
                    "gesture": "highlight-hud",
                    "duration": 9.5
                },
                {
                    "speaker": "senior",
                    "text": "Precisely. In scientific research, predictive models decipher protein folding in minutes rather than decades. AI is fundamentally augmenting human capability across our entire physical and digital infrastructure.",
                    "expression": "inspiring",
                    "gesture": "open-palm",
                    "duration": 13.0
                }
            ]
        },
        {
            "id": 4,
            "name": "Scientific Demonstration Using MATLAB",
            "camera": "cam-matlab-workstation",
            "active_hud": "matlab",
            "is_scientific_demo": True,
            "dialogues": [
                {
                    "speaker": "junior",
                    "text": "Let's examine how a model actually partitions sample space. I've initiated our supervised classification benchmark on MATLAB.",
                    "expression": "engaged",
                    "gesture": "tap-console",
                    "duration": 8.0
                },
                {
                    "speaker": "senior",
                    "text": "Notice how our nearest-neighbor classifier resolves the synthetic decision boundary. By computing Euclidean distances across feature coordinates, it reliably separates class manifolds with verified prediction accuracy.",
                    "expression": "scholarly",
                    "gesture": "point-graph",
                    "duration": 13.0
                },
                {
                    "speaker": "junior",
                    "text": "The confusion matrix verifies robust generalization on the test partition, confirming that foundational geometry drives predictive intelligence.",
                    "expression": "convinced",
                    "gesture": "nod-affirm",
                    "duration": 8.5
                }
            ]
        },
        {
            "id": 5,
            "name": "The Future of AI",
            "camera": "cam-future-tech",
            "active_hud": "future",
            "dialogues": [
                {
                    "speaker": "junior",
                    "text": "Looking forward, where will the next paradigm shift take us? Toward autonomous physical agents or multimodal collaborative intelligence?",
                    "expression": "visionary",
                    "gesture": "inquire",
                    "duration": 8.5
                },
                {
                    "speaker": "senior",
                    "text": "The frontier lies in hybrid neuro-symbolic systems and embodied robotics. We are moving from passive answering models to proactive reasoning partners that collaborate with scientists in real time.",
                    "expression": "visionary",
                    "gesture": "sweeping-hand",
                    "duration": 13.0
                }
            ]
        },
        {
            "id": 6,
            "name": "Ethics and Responsibility",
            "camera": "cam-close-reflection",
            "active_hud": "ethics",
            "dialogues": [
                {
                    "speaker": "junior",
                    "text": "Yet rapid capability introduces critical dilemmas—workforce displacement, algorithmic bias, and the risks of deploying autonomous systems without verifiable safety guarantees.",
                    "expression": "serious",
                    "gesture": "caution",
                    "duration": 9.5
                },
                {
                    "speaker": "senior",
                    "text": "That is why technical innovation must remain indivisible from ethical stewardship. Transparent interpretability, stringent alignment protocols, and continuous human oversight are imperative safeguards for society.",
                    "expression": "resolute",
                    "gesture": "firm-hand",
                    "duration": 12.5
                }
            ]
        },
        {
            "id": 7,
            "name": "Conclusion & Academic Credits",
            "camera": "cam-cinematic-wide",
            "active_hud": "credits",
            "dialogues": [
                {
                    "speaker": "junior",
                    "text": "Ultimately, our machines reflect the goals and values we program into them.",
                    "expression": "thoughtful",
                    "gesture": "nod",
                    "duration": 6.0
                },
                {
                    "speaker": "senior",
                    "text": "Indeed, Marcus. The future of Artificial Intelligence is not simply about creating smarter machines. It is about building technology that helps humanity move forward.",
                    "expression": "inspiring",
                    "gesture": "warm-close",
                    "duration": 12.0
                }
            ]
        }
    ]
}


@app.route("/")
def index():
    """Serves the primary 2D animated research lab presentation interface."""
    return render_template("index.html")


@app.route("/results/<path:filename>")
def serve_results(filename):
    """Serves generated MATLAB PNG graphs, JSON data, and CSV exports."""
    return send_from_directory(RESULTS_DIR, filename)


@app.route("/api/script", methods=["GET"])
def get_script():
    """Returns the authoritative dialogue, timeline, and scene configuration."""
    return jsonify(PRESENTATION_DATA)


@app.route("/api/results", methods=["GET"])
def get_numerical_results():
    """Returns the latest numerical machine learning results."""
    json_path = os.path.join(RESULTS_DIR, "matlab_results.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return jsonify(data)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    return jsonify({"status": "error", "message": "No results found. Execute MATLAB first."}), 404


@app.route("/api/matlab/status", methods=["GET"])
def matlab_status_endpoint():
    """Returns the diagnostics and detection status of the MATLAB environment."""
    return jsonify(get_matlab_status())


@app.route("/api/matlab/run", methods=["POST"])
def run_matlab_endpoint():
    """
    Triggers batch execution of FutureAI.m using actual MATLAB installation.
    Validates resulting PNG and JSON artifacts before responding.
    """
    req_data = request.get_json() or {}
    custom_path = req_data.get("custom_path")
    res = execute_matlab_script(custom_path=custom_path)
    return jsonify(res)


@app.route("/api/matlab/config", methods=["GET", "POST"])
def matlab_config_endpoint():
    """Gets or sets configurable MATLAB installation path."""
    if request.method == "POST":
        data = request.get_json() or {}
        new_path = data.get("matlab_path", "").strip()
        cfg = load_config()
        cfg["matlab_path"] = new_path
        save_config(cfg)
        return jsonify({"status": "success", "config": cfg, "diagnostics": get_matlab_status()})
    return jsonify(load_config())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 70)
    print("  THE FUTURE OF ARTIFICIAL INTELLIGENCE - ACADEMIC RESEARCH LAB")
    print(f"  Starting Flask Service on http://127.0.0.1:{port}")
    print("=" * 70)
    app.run(host="127.0.0.1", port=port, debug=False)
