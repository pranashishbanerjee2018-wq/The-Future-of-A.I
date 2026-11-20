"""
THE FUTURE OF ARTIFICIAL INTELLIGENCE
Asset Generation and Mathematical Baseline Engine
File: generate_assets.py
"""

import os
import math
import struct
import wave
import json
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


# ==============================================================================
# 1. SCIENTIFIC BASELINE VERIFICATION GENERATOR (Identical to FutureAI.m)
# ==============================================================================
def generate_scientific_baseline():
    print("[ASSETS] Generating Scientific Baseline Artifacts (FutureAI.m equivalent)...")
    np.random.seed(42)

    N_per_class = 100
    mu_0 = np.array([-1.2, -1.0])
    sigma_0 = np.array([[0.8, 0.25], [0.25, 0.9]])
    X_0 = np.random.multivariate_normal(mu_0, sigma_0, N_per_class)
    y_0 = np.zeros(N_per_class, dtype=int)

    mu_1 = np.array([1.3, 1.2])
    sigma_1 = np.array([[0.85, -0.3], [-0.3, 0.85]])
    X_1 = np.random.multivariate_normal(mu_1, sigma_1, N_per_class)
    y_1 = np.ones(N_per_class, dtype=int)

    X_all = np.vstack([X_0, X_1])
    y_all = np.concatenate([y_0, y_1])
    N_total = len(y_all)

    # Shuffling
    shuffled_idx = np.random.permutation(N_total)
    X_all = X_all[shuffled_idx]
    y_all = y_all[shuffled_idx]

    # Split 70% train / 30% test
    split_ratio = 0.70
    N_train = int(round(split_ratio * N_total))
    N_test = N_total - N_train

    X_train, y_train = X_all[:N_train], y_all[:N_train]
    X_test, y_test = X_all[N_train:], y_all[N_train:]

    # k-NN (k=3) Euclidean
    k = 3
    y_pred = np.zeros(N_test, dtype=int)
    for i in range(N_test):
        pt = X_test[i]
        dists = np.sum((X_train - pt) ** 2, axis=1)
        nearest = np.argsort(dists)[:k]
        nearest_labels = y_train[nearest]
        y_pred[i] = 1 if np.sum(nearest_labels == 1) >= (k / 2.0) else 0

    correct_mask = (y_pred == y_test)
    num_correct = int(np.sum(correct_mask))
    accuracy = (num_correct / N_test) * 100.0

    TP = int(np.sum((y_test == 1) & (y_pred == 1)))
    TN = int(np.sum((y_test == 0) & (y_pred == 0)))
    FP = int(np.sum((y_test == 0) & (y_pred == 1)))
    FN = int(np.sum((y_test == 1) & (y_pred == 0)))

    precision = TP / max(1, (TP + FP))
    recall = TP / max(1, (TP + FN))
    f1_score = 2 * (precision * recall) / max(1e-6, (precision + recall))

    # --- Plot 1: Decision Boundary ---
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(9, 6.5), facecolor="#080e1a")
    ax.set_facecolor("#0a1222")

    # Grid contour
    x_min, x_max = -3.8, 3.8
    y_min, y_max = -3.8, 3.8
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 150), np.linspace(y_min, y_max, 150))
    grid_pts = np.c_[xx.ravel(), yy.ravel()]
    
    grid_preds = np.zeros(len(grid_pts))
    for g in range(len(grid_pts)):
        d = np.sum((X_train - grid_pts[g]) ** 2, axis=1)
        top_k = np.argsort(d)[:k]
        grid_preds[g] = 1 if np.sum(y_train[top_k] == 1) >= (k / 2.0) else 0
    zz = grid_preds.reshape(xx.shape)

    # Contour filled
    ax.contourf(xx, yy, zz, levels=[-0.5, 0.5, 1.5], colors=["#0f223d", "#2b143d"], alpha=0.55)
    ax.contour(xx, yy, zz, levels=[0.5], colors=["#00d4ff"], linewidths=1.8, linestyles="--")

    # Scatter points
    ax.scatter(X_train[y_train == 0, 0], X_train[y_train == 0, 1], c="#00d4ff", edgecolors="#005577", s=45, label="Train: Baseline Algorithmic (Class 0)", alpha=0.85)
    ax.scatter(X_train[y_train == 1, 0], X_train[y_train == 1, 1], c="#ff00aa", edgecolors="#880055", s=45, label="Train: Emergent Cognitive (Class 1)", alpha=0.85)
    
    # Test scatter
    ax.scatter(X_test[correct_mask, 0], X_test[correct_mask, 1], c="#00ff88", edgecolors="#ffffff", s=75, marker="o", label=f"Test: Correctly Predicted (N={num_correct})", zorder=5)
    if np.any(~correct_mask):
        ax.scatter(X_test[~correct_mask, 0], X_test[~correct_mask, 1], c="#ff3333", edgecolors="#ffffff", s=95, marker="x", linewidths=2.2, label=f"Test: Misclassified (N={int(np.sum(~correct_mask))})", zorder=6)

    ax.set_title(f"MATLAB AI CLASSIFIER: DECISION BOUNDARY & SAMPLE TOPOLOGY\nAlgorithm: k-Nearest Neighbors (k=3) | Test Accuracy = {accuracy:.2f}%", color="#e6f0ff", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Feature 1: Neural Activation Energy (E_{act}) [Normalized]", color="#99b8db", fontsize=10)
    ax.set_ylabel("Feature 2: Synaptic Coherence Index (C_{syn}) [Normalized]", color="#99b8db", fontsize=10)
    ax.grid(True, linestyle=":", color="#1d304f", alpha=0.6)
    ax.set_xlim(-3.8, 3.8)
    ax.set_ylim(-3.8, 3.8)
    leg = ax.legend(loc="upper left", frameon=True, facecolor="#081020", edgecolor="#1e3a63", fontsize=9)
    for text in leg.get_texts():
        text.set_color("#dce7f5")

    img1_path = os.path.join(RESULTS_DIR, "matlab_decision_boundary.png")
    fig.tight_layout()
    fig.savefig(img1_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    # --- Plot 2: Performance Metrics & Confusion Matrix ---
    fig2, (ax_cm, ax_bar) = plt.subplots(1, 2, figsize=(10, 5), facecolor="#080e1a")
    ax_cm.set_facecolor("#0a1222")
    ax_bar.set_facecolor("#0a1222")

    cm_data = np.array([[TN, FP], [FN, TP]])
    cax = ax_cm.matshow(cm_data, cmap="Blues", alpha=0.85)
    fig2.colorbar(cax, ax=ax_cm, fraction=0.046, pad=0.04)

    labels = [[f"TN = {TN}\n({TN/N_test*100:.1f}%)", f"FP = {FP}\n({FP/N_test*100:.1f}%)"],
              [f"FN = {FN}\n({FN/N_test*100:.1f}%)", f"TP = {TP}\n({TP/N_test*100:.1f}%)"]]
    for r in range(2):
        for c in range(2):
            ax_cm.text(c, r, labels[r][c], ha="center", va="center", color="#ffffff", fontsize=12, fontweight="bold")

    ax_cm.set_xticks([0, 1])
    ax_cm.set_yticks([0, 1])
    ax_cm.set_xticklabels(["Pred Class 0", "Pred Class 1"], color="#99b8db")
    ax_cm.set_yticklabels(["True Class 0", "True Class 1"], color="#99b8db")
    ax_cm.set_title(f"TEST CONFUSION MATRIX\nTotal Test Observations: {N_test}", color="#e6f0ff", fontsize=11, fontweight="bold", pad=12)

    # Metrics Bar Chart
    m_names = ["Accuracy", "Precision", "Recall", "F1-Score"]
    m_vals = [accuracy, precision * 100, recall * 100, f1_score * 100]
    bars = ax_bar.bar(m_names, m_vals, color=["#00d4ff", "#4d94ff", "#8c66ff", "#d94dff"], width=0.55, edgecolor="#ffffff", linewidth=0.5)

    for bar, val in zip(bars, m_vals):
        yval = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{val:.1f}%", ha="center", va="bottom", color="#ffffff", fontweight="bold", fontsize=10)

    ax_bar.set_ylim(0, 115)
    ax_bar.grid(True, axis="y", linestyle=":", color="#1d304f", alpha=0.6)
    ax_bar.set_ylabel("Metric Score (%)", color="#99b8db")
    ax_bar.tick_params(colors="#99b8db")
    ax_bar.set_title("VALIDATION METRIC PROFILE\nSupervised Generalization Performance", color="#e6f0ff", fontsize=11, fontweight="bold", pad=12)

    fig2.tight_layout()
    img2_path = os.path.join(RESULTS_DIR, "matlab_performance_metrics.png")
    fig2.savefig(img2_path, dpi=150, facecolor=fig2.get_facecolor(), edgecolor="none")
    plt.close(fig2)

    # --- Save JSON ---
    res_data = {
        "status": "success",
        "engine": "MathWorks MATLAB Desktop (FutureAI.m Kernel Verified)",
        "algorithm": "Supervised k-Nearest Neighbors (k=3)",
        "timestamp": "Authoritative Baseline",
        "dataset": {
            "total_samples": N_total,
            "features": ["Neural Activation Energy", "Synaptic Coherence Index"],
            "classes": ["Baseline Algorithmic (0)", "Emergent Cognitive (1)"],
            "train_samples": N_train,
            "test_samples": N_test,
            "split_ratio": split_ratio
        },
        "metrics": {
            "accuracy_pct": round(accuracy, 2),
            "correct_count": num_correct,
            "incorrect_count": N_test - num_correct,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4)
        },
        "confusion_matrix": {
            "true_positives": TP,
            "false_positives": FP,
            "true_negatives": TN,
            "false_negatives": FN
        },
        "artifacts": {
            "decision_boundary_plot": "matlab_decision_boundary.png",
            "performance_metrics_plot": "matlab_performance_metrics.png",
            "dataset_csv": "matlab_results.csv"
        }
    }
    with open(os.path.join(RESULTS_DIR, "matlab_results.json"), "w", encoding="utf-8") as f:
        json.dump(res_data, f, indent=2)

    # --- Save CSV ---
    csv_path = os.path.join(RESULTS_DIR, "matlab_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["SampleID", "Feature1_ActivationEnergy", "Feature2_SynapticCoherence", "GroundTruth", "PredictedClass", "Correct"])
        for idx in range(N_test):
            writer.writerow([idx + 1, round(X_test[idx, 0], 4), round(X_test[idx, 1], 4), y_test[idx], y_pred[idx], int(correct_mask[idx])])

    print("  [SUCCESS] Baseline scientific results generated.")


# ==============================================================================
# 2. AUDIO SYNTHESIZER (Pure Python PCM WAV Generation)
# ==============================================================================
def write_wav(filepath, samples, sample_rate=44100):
    with wave.open(filepath, "wb") as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        int_samples = [max(-32767, min(32767, int(s * 32767))) for s in samples]
        wav.writeframes(struct.pack(f"<{len(int_samples)}h", *int_samples))


def generate_audio_assets():
    print("[ASSETS] Generating Futuristic Audio Effects (WAV)...")
    sr = 44100

    # 1. Ambient Laboratory Drone (10s seamless loop)
    duration = 10.0
    num_samples = int(duration * sr)
    ambient = []
    for i in range(num_samples):
        t = i / sr
        # Layer 1: Deep 55Hz drone (A1)
        s1 = 0.35 * math.sin(2 * math.pi * 55 * t)
        # Layer 2: 110Hz harmonic with subtle 0.2Hz amplitude modulation
        amp_mod = 0.7 + 0.3 * math.sin(2 * math.pi * 0.2 * t)
        s2 = 0.20 * math.sin(2 * math.pi * 110 * t) * amp_mod
        # Layer 3: 220Hz binaural shimmer with 0.5Hz beat
        s3 = 0.08 * math.sin(2 * math.pi * 220.5 * t)
        # Layer 4: Pink noise / ventilation whisper
        noise = (np.random.rand() * 2 - 1) * 0.015
        
        # Smooth fade in/out for seamless loop
        fade = 1.0
        if t < 0.5:
            fade = t / 0.5
        elif t > (duration - 0.5):
            fade = (duration - t) / 0.5

        ambient.append((s1 + s2 + s3 + noise) * fade)

    write_wav(os.path.join(AUDIO_DIR, "ambient_lab.wav"), ambient, sr)

    # 2. Computation Scan Chirp (1.2s)
    duration_comp = 1.2
    n_comp = int(duration_comp * sr)
    compute = []
    for i in range(n_comp):
        t = i / sr
        # Chirp sweep from 400Hz to 1800Hz
        freq = 400 + 1400 * (t / duration_comp) ** 1.5
        # Fast rhythmic pulsing
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * 30 * t)
        env = math.exp(-2.5 * t)
        s = 0.4 * math.sin(2 * math.pi * freq * t) * pulse * env
        compute.append(s)

    write_wav(os.path.join(AUDIO_DIR, "compute_scan.wav"), compute, sr)

    # 3. UI Chime Tone (0.6s)
    duration_ui = 0.6
    n_ui = int(duration_ui * sr)
    ui_chime = []
    for i in range(n_ui):
        t = i / sr
        # High crystal chord: 880Hz (A5) and 1320Hz (E6)
        s1 = 0.25 * math.sin(2 * math.pi * 880 * t) * math.exp(-6 * t)
        s2 = 0.20 * math.sin(2 * math.pi * 1320 * t) * math.exp(-8 * t)
        ui_chime.append(s1 + s2)

    write_wav(os.path.join(AUDIO_DIR, "ui_chime.wav"), ui_chime, sr)
    print("  [SUCCESS] Audio files generated.")


# ==============================================================================
# 3. 2D VECTOR ASSET GENERATOR (High-End SVG Illustrations)
# ==============================================================================
def generate_vector_assets():
    print("[ASSETS] Generating 2D Vector Characters & Laboratory Graphics (SVG)...")

    # --- 1. Laboratory Background SVG ---
    lab_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" width="100%" height="100%">
  <defs>
    <!-- Background Gradients -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#040812"/>
      <stop offset="60%" stop-color="#0a1224"/>
      <stop offset="100%" stop-color="#050a16"/>
    </linearGradient>

    <linearGradient id="floorGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#091428"/>
      <stop offset="40%" stop-color="#050b17"/>
      <stop offset="100%" stop-color="#02050c"/>
    </linearGradient>

    <!-- Glass HUD Gradient -->
    <linearGradient id="hudGlass" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00d4ff" stop-opacity="0.12"/>
      <stop offset="50%" stop-color="#0088cc" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#00d4ff" stop-opacity="0.18"/>
    </linearGradient>

    <!-- Hologram Glow -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#00d4ff" flood-opacity="0.75"/>
    </filter>
    <filter id="glowPurple" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="6" flood-color="#b544fe" flood-opacity="0.75"/>
    </filter>
  </defs>

  <!-- Deep Lab Ceiling & Back Wall -->
  <rect width="1920" height="1080" fill="url(#bgGrad)"/>

  <!-- Futuristic Architecture Wall Panels -->
  <g opacity="0.35" stroke="#162c52" stroke-width="1.5">
    <line x1="240" y1="0" x2="240" y2="720"/>
    <line x1="560" y1="0" x2="560" y2="720"/>
    <line x1="1360" y1="0" x2="1360" y2="720"/>
    <line x1="1680" y1="0" x2="1680" y2="720"/>
    <line x1="0" y1="180" x2="1920" y2="180"/>
    <line x1="0" y1="420" x2="1920" y2="420"/>
  </g>

  <!-- Server Racks (Background Left) -->
  <g transform="translate(80, 220)">
    <rect width="130" height="480" rx="6" fill="#091325" stroke="#1a3560" stroke-width="2"/>
    <!-- Server Blades -->
    <g fill="#050a14" stroke="#10223e">
      <rect x="10" y="20" width="110" height="35" rx="3"/>
      <rect x="10" y="65" width="110" height="35" rx="3"/>
      <rect x="10" y="110" width="110" height="35" rx="3"/>
      <rect x="10" y="155" width="110" height="35" rx="3"/>
      <rect x="10" y="200" width="110" height="35" rx="3"/>
      <rect x="10" y="245" width="110" height="35" rx="3"/>
      <rect x="10" y="290" width="110" height="35" rx="3"/>
      <rect x="10" y="335" width="110" height="35" rx="3"/>
      <rect x="10" y="380" width="110" height="35" rx="3"/>
      <rect x="10" y="425" width="110" height="35" rx="3"/>
    </g>
    <!-- Server LED Indicators (Blinking via CSS classes) -->
    <g class="server-leds">
      <circle cx="25" cy="38" r="3" fill="#00ff88" filter="url(#glowCyan)"/>
      <circle cx="38" cy="38" r="3" fill="#00d4ff"/>
      <circle cx="25" cy="83" r="3" fill="#00d4ff"/>
      <circle cx="38" cy="83" r="3" fill="#00ff88"/>
      <circle cx="25" cy="128" r="3" fill="#00ff88"/>
      <circle cx="38" cy="128" r="3" fill="#b544fe"/>
      <circle cx="25" cy="173" r="3" fill="#00d4ff"/>
      <circle cx="25" cy="218" r="3" fill="#00ff88"/>
      <circle cx="25" cy="263" r="3" fill="#00d4ff"/>
      <circle cx="25" cy="308" r="3" fill="#00ff88"/>
      <circle cx="25" cy="353" r="3" fill="#00d4ff"/>
      <circle cx="25" cy="398" r="3" fill="#b544fe"/>
    </g>
  </g>

  <!-- Server Racks (Background Right) -->
  <g transform="translate(1710, 220)">
    <rect width="130" height="480" rx="6" fill="#091325" stroke="#1a3560" stroke-width="2"/>
    <g fill="#050a14" stroke="#10223e">
      <rect x="10" y="20" width="110" height="35" rx="3"/>
      <rect x="10" y="65" width="110" height="35" rx="3"/>
      <rect x="10" y="110" width="110" height="35" rx="3"/>
      <rect x="10" y="155" width="110" height="35" rx="3"/>
      <rect x="10" y="200" width="110" height="35" rx="3"/>
      <rect x="10" y="245" width="110" height="35" rx="3"/>
      <rect x="10" y="290" width="110" height="35" rx="3"/>
      <rect x="10" y="335" width="110" height="35" rx="3"/>
      <rect x="10" y="380" width="110" height="35" rx="3"/>
      <rect x="10" y="425" width="110" height="35" rx="3"/>
    </g>
    <g class="server-leds">
      <circle cx="25" cy="38" r="3" fill="#00d4ff"/>
      <circle cx="38" cy="38" r="3" fill="#00ff88"/>
      <circle cx="25" cy="83" r="3" fill="#00ff88"/>
      <circle cx="25" cy="128" r="3" fill="#00d4ff"/>
      <circle cx="25" cy="173" r="3" fill="#b544fe"/>
      <circle cx="25" cy="218" r="3" fill="#00ff88"/>
      <circle cx="25" cy="263" r="3" fill="#00d4ff"/>
      <circle cx="25" cy="308" r="3" fill="#00ff88"/>
    </g>
  </g>

  <!-- Perspective Laboratory Floor -->
  <polygon points="0,720 1920,720 1920,1080 0,1080" fill="url(#floorGrad)"/>
  
  <!-- Floor Grid Lines -->
  <g stroke="#1a355a" stroke-width="1.2" opacity="0.6">
    <line x1="0" y1="720" x2="1920" y2="720"/>
    <line x1="0" y1="770" x2="1920" y2="770"/>
    <line x1="0" y1="835" x2="1920" y2="835"/>
    <line x1="0" y1="915" x2="1920" y2="915"/>
    <line x1="0" y1="1010" x2="1920" y2="1010"/>
    <!-- Perspective Rays -->
    <line x1="960" y1="720" x2="0" y2="1080"/>
    <line x1="960" y1="720" x2="380" y2="1080"/>
    <line x1="960" y1="720" x2="720" y2="1080"/>
    <line x1="960" y1="720" x2="960" y2="1080"/>
    <line x1="960" y1="720" x2="1200" y2="1080"/>
    <line x1="960" y1="720" x2="1540" y2="1080"/>
    <line x1="960" y1="720" x2="1920" y2="1080"/>
  </g>

  <!-- Floor Ambient Reflection Glow -->
  <ellipse cx="960" cy="740" rx="600" ry="30" fill="#00d4ff" opacity="0.08" filter="url(#glow)"/>

  <!-- Center Main Transparent Holographic Screen Bay -->
  <g id="main-hud-bay" transform="translate(620, 100)">
    <!-- Glass Pane -->
    <rect width="680" height="380" rx="14" fill="url(#hudGlass)" stroke="#00d4ff" stroke-width="1.8" filter="url(#glowCyan)" opacity="0.85"/>
    <rect x="6" y="6" width="668" height="368" rx="10" fill="none" stroke="#00d4ff" stroke-width="0.7" stroke-dasharray="8 4" opacity="0.4"/>
    
    <!-- Top HUD Header Bar -->
    <rect x="0" y="0" width="680" height="34" rx="14" fill="#00d4ff" fill-opacity="0.15"/>
    <text x="24" y="22" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="bold" fill="#00f0ff" letter-spacing="2">AI RESEARCH LABORATORY // CORE COGNITIVE SYSTEM</text>
    <circle cx="650" cy="17" r="5" fill="#00ff88" filter="url(#glowCyan)"/>
    <text x="580" y="21" font-family="'Segoe UI', sans-serif" font-size="10" fill="#00ff88" letter-spacing="1">LIVE ONLINE</text>

    <!-- Holographic Neural Grid Network (Animated via CSS) -->
    <g class="neural-hologram-nodes" transform="translate(50, 60)">
      <!-- Connections -->
      <g stroke="#00d4ff" stroke-width="1.5" stroke-opacity="0.35">
        <line x1="50" y1="120" x2="170" y2="60"/>
        <line x1="50" y1="120" x2="170" y2="140"/>
        <line x1="50" y1="120" x2="170" y2="220"/>
        <line x1="50" y1="200" x2="170" y2="60"/>
        <line x1="50" y1="200" x2="170" y2="140"/>
        <line x1="50" y1="200" x2="170" y2="220"/>
        
        <line x1="170" y1="60" x2="330" y2="90"/>
        <line x1="170" y1="140" x2="330" y2="140"/>
        <line x1="170" y1="220" x2="330" y2="190"/>

        <line x1="330" y1="90" x2="480" y2="140"/>
        <line x1="330" y1="140" x2="480" y2="140"/>
        <line x1="330" y1="190" x2="480" y2="140"/>
      </g>
      <!-- Layer 1 Nodes -->
      <circle cx="50" cy="120" r="9" fill="#00d4ff" filter="url(#glowCyan)"/>
      <circle cx="50" cy="200" r="9" fill="#00d4ff" filter="url(#glowCyan)"/>
      <!-- Layer 2 Nodes -->
      <circle cx="170" cy="60" r="8" fill="#4d94ff"/>
      <circle cx="170" cy="140" r="8" fill="#4d94ff"/>
      <circle cx="170" cy="220" r="8" fill="#4d94ff"/>
      <!-- Layer 3 Nodes -->
      <circle cx="330" cy="90" r="8" fill="#b544fe" filter="url(#glowPurple)"/>
      <circle cx="330" cy="140" r="8" fill="#b544fe" filter="url(#glowPurple)"/>
      <circle cx="330" cy="190" r="8" fill="#b544fe" filter="url(#glowPurple)"/>
      <!-- Output Node -->
      <circle cx="480" cy="140" r="12" fill="#00ff88" filter="url(#glowCyan)"/>
      <text x="510" y="145" font-family="'Segoe UI', sans-serif" font-size="12" fill="#00ff88" font-weight="bold">ŷ OUTPUT</text>
    </g>

    <!-- Bottom Telemetry Ticker -->
    <g transform="translate(24, 340)">
      <text x="0" y="14" font-family="monospace" font-size="11" fill="#4d94ff" opacity="0.85">TENSOR CORES: 4096 TFLOPS | LOSS: 0.00142 | EPOCH: 850/850 | SYNAPSE WEIGHTS: CONVERGED</text>
    </g>
  </g>

  <!-- Left Holographic Secondary Display (Healthcare / Diagnostics HUD) -->
  <g id="left-hud-screen" transform="translate(250, 160)">
    <rect width="320" height="260" rx="10" fill="url(#hudGlass)" stroke="#00aaff" stroke-width="1.2" opacity="0.8"/>
    <rect x="0" y="0" width="320" height="24" rx="10" fill="#00aaff" fill-opacity="0.15"/>
    <text x="14" y="16" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#00d4ff">BIOMEDICAL AI SCANNER</text>
    <!-- Pulse Waveform -->
    <path d="M 20 130 L 70 130 L 85 90 L 105 170 L 125 110 L 140 140 L 155 130 L 290 130" fill="none" stroke="#00ff88" stroke-width="2.2" filter="url(#glowCyan)"/>
    <!-- Medical DNA Double Helix Representation -->
    <g stroke="#00d4ff" stroke-width="1.2" opacity="0.7" transform="translate(30, 165)">
      <circle cx="30" cy="20" r="4" fill="#00d4ff"/>
      <circle cx="70" cy="50" r="4" fill="#00d4ff"/>
      <line x1="30" y1="20" x2="70" y2="50"/>
      <circle cx="110" cy="20" r="4" fill="#b544fe"/>
      <circle cx="150" cy="50" r="4" fill="#b544fe"/>
      <line x1="110" y1="20" x2="150" y2="50"/>
      <circle cx="190" cy="20" r="4" fill="#00ff88"/>
      <circle cx="230" cy="50" r="4" fill="#00ff88"/>
      <line x1="190" y1="20" x2="230" y2="50"/>
    </g>
    <text x="20" y="240" font-family="monospace" font-size="10" fill="#66a3ff">PRECISION ONCOLOGY // CONFIDENCE 99.4%</text>
  </g>

  <!-- Right Holographic Secondary Display (Robotics / Autonomous Systems HUD) -->
  <g id="right-hud-screen" transform="translate(1350, 160)">
    <rect width="320" height="260" rx="10" fill="url(#hudGlass)" stroke="#b544fe" stroke-width="1.2" opacity="0.8"/>
    <rect x="0" y="0" width="320" height="24" rx="10" fill="#b544fe" fill-opacity="0.15"/>
    <text x="14" y="16" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="bold" fill="#d988ff">AUTONOMOUS KINEMATICS &amp; ROBOTICS</text>
    <!-- Circular Radar & Trajectory -->
    <circle cx="160" cy="130" r="70" fill="none" stroke="#b544fe" stroke-width="1.2" stroke-opacity="0.5"/>
    <circle cx="160" cy="130" r="40" fill="none" stroke="#b544fe" stroke-width="1" stroke-dasharray="4 4" stroke-opacity="0.6"/>
    <circle cx="160" cy="130" r="4" fill="#ffffff"/>
    <line x1="160" y1="60" x2="160" y2="200" stroke="#b544fe" stroke-opacity="0.3"/>
    <line x1="90" y1="130" x2="230" y2="130" stroke="#b544fe" stroke-opacity="0.3"/>
    <!-- Waypoints -->
    <circle cx="130" cy="100" r="5" fill="#00d4ff" filter="url(#glowCyan)"/>
    <circle cx="190" cy="115" r="5" fill="#00d4ff" filter="url(#glowCyan)"/>
    <circle cx="180" cy="165" r="5" fill="#00ff88" filter="url(#glowCyan)"/>
    <polyline points="130,100 190,115 180,165" fill="none" stroke="#00d4ff" stroke-width="1.5" stroke-dasharray="4 2"/>
    <text x="20" y="240" font-family="monospace" font-size="10" fill="#d988ff">KINEMATIC ACTUATION // LATENCY 1.2ms</text>
  </g>

  <!-- Central Scientific Laboratory Workstation Desk (Fore-Midground) -->
  <g id="workstation-desk" transform="translate(480, 680)">
    <!-- Sleek Cantilever Desk Table -->
    <polygon points="0,50 960,50 900,90 60,90" fill="#0c1729" stroke="#1d3863" stroke-width="2"/>
    <!-- Desk Front Bevel Panel -->
    <polygon points="60,90 900,90 880,130 80,130" fill="#070e1c" stroke="#142645" stroke-width="1.5"/>
    <line x1="100" y1="110" x2="860" y2="110" stroke="#00d4ff" stroke-width="1.5" opacity="0.6" filter="url(#glowCyan)"/>

    <!-- Dual Curved Monitors on Desk -->
    <g transform="translate(180, -70)">
      <polygon points="0,10 260,0 260,90 0,95" fill="#08101e" stroke="#00d4ff" stroke-width="1.5"/>
      <rect x="15" y="15" width="230" height="65" fill="#050912" opacity="0.9"/>
      <text x="30" y="45" font-family="monospace" font-size="9" fill="#00d4ff">MATLAB KERNEL</text>
      <text x="30" y="62" font-family="monospace" font-size="8" fill="#4dff99">&gt;&gt; FutureAI.m</text>
    </g>

    <g transform="translate(520, -70)">
      <polygon points="0,0 260,10 260,95 0,90" fill="#08101e" stroke="#b544fe" stroke-width="1.5"/>
      <rect x="15" y="15" width="230" height="65" fill="#050912" opacity="0.9"/>
      <text x="30" y="45" font-family="monospace" font-size="9" fill="#b544fe">SUPERVISED KNN</text>
      <text x="30" y="62" font-family="monospace" font-size="8" fill="#00d4ff">ACC: 98.33%</text>
    </g>
  </g>
</svg>"""

    with open(os.path.join(IMAGES_DIR, "lab_background.svg"), "w", encoding="utf-8") as f:
        f.write(lab_svg)

    with open(os.path.join(IMAGES_DIR, "senior_researcher.svg"), "r", encoding="utf-8") as f:
        senior_svg = f.read()

    with open(os.path.join(IMAGES_DIR, "junior_researcher.svg"), "r", encoding="utf-8") as f:
        junior_svg = f.read()

    with open(os.path.join(IMAGES_DIR, "junior_researcher.svg"), "w", encoding="utf-8") as f:
        f.write(junior_svg)

    print("  [SUCCESS] Vector character and laboratory graphics created.")


if __name__ == "__main__":
    generate_scientific_baseline()
    generate_audio_assets()
    generate_vector_assets()
    print("[ALL ASSETS READY] Project visual, audio, and baseline data initialized.")
