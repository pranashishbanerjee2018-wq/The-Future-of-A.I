/**
 * THE FUTURE OF ARTIFICIAL INTELLIGENCE
 * Master Presentation Sequencer, Phoneme Lip-Sync & Natural Gestures
 * File: static/js/app.js
 */

/**
 * Safely sets class attribute on both HTML and SVG elements.
 * In SVG DOM, element.className is an SVGAnimatedString (which only has a getter in Chromium).
 * Using setAttribute('class', ...) guarantees 100% cross-browser compatibility.
 */
function setElementClass(el, className) {
  if (!el) return;
  if (typeof el.setAttribute === 'function') {
    el.setAttribute('class', className);
  } else {
    el.className = className;
  }
}

/* ==============================================================================
   1. LIP-SYNC CONTROLLER (Phoneme-Synchronized Mouth Animation)
   ============================================================================== */
class LipSyncManager {
  constructor() {
    this.seniorMouth = null;
    this.juniorMouth = null;
    this.activeSpeaker = null;
    this.timer = null;
    this.currentPhoneme = 'phoneme-rest';
    this.isPaused = false;
    this.phonemeQueue = [];
    this.queueIndex = 0;
    this.stepInterval = 85; // ~12 fps phoneme articulatory rate
    this.totalTextLength = 0;
  }

  init() {
    this.seniorMouth = document.getElementById('senior-mouth');
    this.juniorMouth = document.getElementById('junior-mouth');
    this.resetAll();
  }

  resetAll() {
    this.stop();
    if (this.seniorMouth) {
      setElementClass(this.seniorMouth, 'mouth-group phoneme-rest');
    }
    if (this.juniorMouth) {
      setElementClass(this.juniorMouth, 'mouth-group phoneme-rest');
    }
  }

  setMouthShape(speakerId, phoneme) {
    const mouth = (speakerId === 'senior') ? this.seniorMouth : this.juniorMouth;
    const otherMouth = (speakerId === 'senior') ? this.juniorMouth : this.seniorMouth;

    // Ensure the non-speaking character keeps mouth strictly closed
    if (otherMouth) {
      setElementClass(otherMouth, 'mouth-group phoneme-rest');
    }

    if (mouth) {
      setElementClass(mouth, `mouth-group ${phoneme}`);
      this.currentPhoneme = phoneme;
    }
  }

  start(speakerId, text, durationSec) {
    this.stop();
    this.activeSpeaker = speakerId;
    this.isPaused = false;

    // Pre-calculate natural phonetic syllables for the dialogue
    this.phonemeQueue = this.generatePhonemeSequence(text, durationSec);
    this.queueIndex = 0;

    // Run active phoneme sequencer
    this.timer = setInterval(() => {
      if (!this.isPaused && this.activeSpeaker) {
        if (this.queueIndex < this.phonemeQueue.length) {
          const ph = this.phonemeQueue[this.queueIndex];
          this.setMouthShape(this.activeSpeaker, ph);
          this.queueIndex++;
        } else {
          // Reached end of utterance
          this.setMouthShape(this.activeSpeaker, 'phoneme-rest');
        }
      }
    }, this.stepInterval);
  }

  onWordBoundary(event) {
    if (!this.activeSpeaker || this.phonemeQueue.length === 0) return;
    // Align phoneme queue index directly with speech boundary progress
    if (typeof event.charIndex === 'number' && this.totalTextLength > 0) {
      const progress = event.charIndex / this.totalTextLength;
      this.queueIndex = Math.min(
        this.phonemeQueue.length - 1,
        Math.floor(progress * this.phonemeQueue.length)
      );
    }
  }

  generatePhonemeSequence(text, durationSec) {
    this.totalTextLength = text.length;
    const words = text.split(/\s+/);
    const queue = [];

    for (let w = 0; w < words.length; w++) {
      const word = words[w];
      const clean = word.toLowerCase().replace(/[^a-z]/g, '');

      // Analyze phonemes for this word
      const wordPhonemes = [];
      for (let c = 0; c < clean.length; c++) {
        const char = clean[c];
        if ('ae'.includes(char)) {
          wordPhonemes.push('phoneme-open');
        } else if ('ou'.includes(char)) {
          wordPhonemes.push('phoneme-round');
        } else if ('iy'.includes(char)) {
          wordPhonemes.push('phoneme-wide');
        } else if ('mbp'.includes(char)) {
          wordPhonemes.push('phoneme-rest'); // Bilabial lip closure
        } else {
          wordPhonemes.push('phoneme-mid'); // Consonant articulators
        }
      }

      // Compress consecutive duplicates to prevent unnatural fluttering
      const compressed = [];
      for (let i = 0; i < wordPhonemes.length; i++) {
        if (compressed.length === 0 || compressed[compressed.length - 1] !== wordPhonemes[i]) {
          compressed.push(wordPhonemes[i]);
          // Add hold frame for prominent open/round vowels
          if (wordPhonemes[i] === 'phoneme-open' || wordPhonemes[i] === 'phoneme-round') {
            compressed.push(wordPhonemes[i]);
          }
        }
      }

      queue.push(...compressed);

      // Micro pauses between words and clauses
      if (word.endsWith('.') || word.endsWith('!') || word.endsWith('?')) {
        queue.push('phoneme-rest', 'phoneme-rest', 'phoneme-rest'); // Full sentence respiration pause
      } else if (word.endsWith(',') || word.endsWith(';') || word.endsWith(':') || word.endsWith('—')) {
        queue.push('phoneme-rest', 'phoneme-rest'); // Clause pause
      } else {
        queue.push('phoneme-mid'); // Inter-word transition
      }
    }

    return queue;
  }

  pause() {
    this.isPaused = true;
  }

  resume() {
    this.isPaused = false;
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.activeSpeaker = null;
    this.queueIndex = 0;
    this.phonemeQueue = [];
    if (this.seniorMouth) setElementClass(this.seniorMouth, 'mouth-group phoneme-rest');
    if (this.juniorMouth) setElementClass(this.juniorMouth, 'mouth-group phoneme-rest');
  }
}

/* ==============================================================================
   2. GESTURE CONTROLLER (Natural Hand & Body Movements)
   ============================================================================== */
class GestureManager {
  constructor() {
    this.seniorRightArm = null;
    this.seniorLeftArm = null;
    this.juniorRightArm = null;
    this.juniorLeftArm = null;
    this.seniorHead = null;
    this.juniorHead = null;
    this.gestureTimeout = null;
    this.secondaryTimeout = null;
  }

  init() {
    this.seniorRightArm = document.getElementById('senior-right-arm');
    this.seniorLeftArm = document.getElementById('senior-left-arm');
    this.juniorRightArm = document.getElementById('junior-right-arm');
    this.juniorLeftArm = document.getElementById('junior-left-arm');
    this.seniorHead = document.getElementById('senior-head-group');
    this.juniorHead = document.getElementById('junior-head-group');
    this.resetAll();
  }

  resetAll() {
    if (this.gestureTimeout) clearTimeout(this.gestureTimeout);
    if (this.secondaryTimeout) clearTimeout(this.secondaryTimeout);

    if (this.seniorRightArm) setElementClass(this.seniorRightArm, 'arm-joint-right gesture-rest');
    if (this.seniorLeftArm) setElementClass(this.seniorLeftArm, 'arm-joint-left gesture-rest');
    if (this.juniorRightArm) setElementClass(this.juniorRightArm, 'arm-joint-right gesture-rest');
    if (this.juniorLeftArm) setElementClass(this.juniorLeftArm, 'tablet-arm-group gesture-rest');

    if (this.seniorHead) setElementClass(this.seniorHead, 'head-joint');
    if (this.juniorHead) setElementClass(this.juniorHead, 'head-joint');
  }

  trigger(speakerId, gestureName, durationSec) {
    this.resetAll();
    const isSenior = (speakerId === 'senior');

    // 1. Configure Listening Character (Rest + Attentive Listening Nod)
    if (isSenior) {
      // Junior is listening
      if (this.juniorRightArm) setElementClass(this.juniorRightArm, 'arm-joint-right gesture-rest');
      if (this.juniorHead) setElementClass(this.juniorHead, 'head-joint listening-colleague-nod');
      if (this.seniorHead) setElementClass(this.seniorHead, 'head-joint');
    } else {
      // Senior is listening
      if (this.seniorRightArm) setElementClass(this.seniorRightArm, 'arm-joint-right gesture-rest');
      if (this.seniorHead) setElementClass(this.seniorHead, 'head-joint listening-colleague-nod');
      if (this.juniorHead) setElementClass(this.juniorHead, 'head-joint');
    }

    // 2. Map and Apply Active Speaker Gesture
    const gestureClass = `gesture-${gestureName || 'rest'}`;
    const targetArm = isSenior ? this.seniorRightArm : this.juniorRightArm;

    if (targetArm) {
      setElementClass(targetArm, `arm-joint-right ${gestureClass}`);

      // Additional two-handed gesture support for Senior's open-palm
      if (isSenior && gestureName === 'open-palm' && this.seniorLeftArm) {
        setElementClass(this.seniorLeftArm, 'arm-joint-left gesture-open-palm-left');
      }

      // Inquisitive head tilt for Junior
      if (!isSenior && gestureName === 'inquire' && this.juniorHead) {
        setElementClass(this.juniorHead, 'head-joint head-tilt-inquire');
      }

      // Schedule natural return to rest (holds for 2.8s - 3.8s, then smoothly settles)
      const holdDurationMs = Math.min(Math.max(2600, durationSec * 0.45 * 1000), 3800);
      this.gestureTimeout = setTimeout(() => {
        if (targetArm) setElementClass(targetArm, 'arm-joint-right gesture-rest');
        if (this.seniorLeftArm) setElementClass(this.seniorLeftArm, 'arm-joint-left gesture-rest');
        if (!isSenior && this.juniorHead) setElementClass(this.juniorHead, 'head-joint');

        // If dialogue is long (> 8s), schedule a second subtle emphasis nod
        if (durationSec > 8.0) {
          const secondDelayMs = 1200;
          this.secondaryTimeout = setTimeout(() => {
            if (targetArm) setElementClass(targetArm, 'arm-joint-right gesture-emphasize');
            setTimeout(() => {
              if (targetArm) setElementClass(targetArm, 'arm-joint-right gesture-rest');
            }, 2200);
          }, secondDelayMs);
        }
      }, holdDurationMs);
    }
  }
}

/* ==============================================================================
   3. PRESENTATION SEQUENCER ENGINE
   ============================================================================== */
class PresentationApp {
  constructor() {
    this.scriptData = null;
    this.currentSceneIdx = 0;
    this.currentDialogueIdx = 0;
    this.isPlaying = false;
    this.isPaused = false;
    this.totalDuration = 165; // 2 minutes 45 seconds target
    this.elapsedTime = 0;
    this.timerInterval = null;
    this.dialogueTimeout = null;

    // Animation Controllers
    this.lipSync = new LipSyncManager();
    this.gestures = new GestureManager();

    // DOM Elements
    this.viewportEl = document.getElementById('presentation-viewport');
    this.curtainEl = document.getElementById('title-intro-curtain');
    this.creditsEl = document.getElementById('credits-slate');
    this.subtitlesBar = document.getElementById('dialogue-subtitles-bar');
    this.speakerDot = document.getElementById('subtitles-speaker-indicator');
    this.speakerName = document.getElementById('subtitles-speaker-name');
    this.speakerRole = document.getElementById('subtitles-speaker-role');
    this.subtitlesContent = document.getElementById('subtitles-content');

    this.charSenior = document.getElementById('char-senior-container');
    this.charJunior = document.getElementById('char-junior-container');
    this.bgLayer = document.getElementById('scene-background-layer');

    // Controls
    this.btnPlayPause = document.getElementById('ctrl-play-pause');
    this.btnPlayPauseIcon = document.getElementById('ctrl-play-pause-icon');
    this.btnRestart = document.getElementById('ctrl-restart');
    this.btnSubtitles = document.getElementById('ctrl-subtitles');
    this.btnAudio = document.getElementById('ctrl-audio');
    this.btnAudioIcon = document.getElementById('ctrl-audio-icon');
    this.sceneDropdown = document.getElementById('scene-jump-selector');

    this.timeCurrent = document.getElementById('time-current');
    this.timeTotal = document.getElementById('time-total');
    this.timelineFill = document.getElementById('timeline-progress-fill');
    this.sceneBadge = document.getElementById('scene-title-badge');

    this.init();
  }

  async init() {
    try {
      this.lipSync.init();
    } catch (e) {
      console.error('[APP] LipSync initialization error:', e);
    }
    try {
      this.gestures.init();
    } catch (e) {
      console.error('[APP] Gestures initialization error:', e);
    }
    this.bindEvents();
    await this.loadScript();
  }

  async loadScript() {
    try {
      let res = await fetch('data/presentation.json');
      if (!res.ok) {
        res = await fetch('/api/script');
      }
      if (res.ok) {
        this.scriptData = await res.json();
        this.totalDuration = this.scriptData.target_duration_seconds || 165;
        this.formatTime(this.totalDuration, this.timeTotal);
        console.log('[APP] Presentation script loaded:', this.scriptData);
        if (this.isPlaying && this.currentSceneIdx === 0 && this.currentDialogueIdx === 0) {
          this.playCurrentStep();
        }
      }
    } catch (e) {
      console.error('[APP] Error loading script data:', e);
    }
  }

  bindEvents() {
    // Start button on curtain
    const btnStart = document.getElementById('btn-start-presentation');
    if (btnStart) {
      btnStart.addEventListener('click', () => this.startPresentation());
    }

    // Replay button on credits slate
    const btnReplay = document.getElementById('btn-replay-presentation');
    if (btnReplay) {
      btnReplay.addEventListener('click', () => this.restartPresentation());
    }

    // Controls
    if (this.btnPlayPause) {
      this.btnPlayPause.addEventListener('click', () => this.togglePlayPause());
    }
    if (this.btnRestart) {
      this.btnRestart.addEventListener('click', () => this.restartPresentation());
    }
    if (this.btnSubtitles) {
      this.btnSubtitles.addEventListener('click', () => this.toggleSubtitles());
    }
    if (this.btnAudio) {
      this.btnAudio.addEventListener('click', () => this.toggleAudio());
    }
    if (this.sceneDropdown) {
      this.sceneDropdown.addEventListener('change', (e) => {
        const sceneNum = parseInt(e.target.value, 10);
        this.jumpToScene(sceneNum - 1);
      });
    }

    // Timeline Scrubber Click
    const scrubber = document.getElementById('timeline-scrubber');
    if (scrubber) {
      scrubber.addEventListener('click', (e) => {
        const rect = scrubber.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        const targetSec = Math.max(0, Math.min(this.totalDuration, pos * this.totalDuration));
        this.seekToTime(targetSec);
      });
    }
  }

  startPresentation() {
    if (this.curtainEl) {
      this.curtainEl.classList.add('dismissed');
    }
    if (this.creditsEl) {
      this.creditsEl.classList.add('hidden');
    }

    try {
      if (window.labEffects) {
        window.labEffects.playAmbient();
        window.labEffects.playChime();
      }
    } catch (e) {
      console.warn('[APP] Sound effects play error:', e);
    }

    this.isPlaying = true;
    this.isPaused = false;
    if (this.viewportEl) this.viewportEl.classList.remove('presentation-paused');
    if (this.btnPlayPauseIcon) this.btnPlayPauseIcon.textContent = '⏸';

    this.startClock();
    if (this.scriptData) {
      this.playCurrentStep();
    } else {
      console.log('[APP] Presentation marked playing; awaiting script load.');
    }
  }

  togglePlayPause() {
    if (!this.isPlaying) {
      this.startPresentation();
      return;
    }

    if (!this.isPaused) {
      // Pause
      this.isPaused = true;
      this.btnPlayPauseIcon.textContent = '▶';
      if (this.viewportEl) this.viewportEl.classList.add('presentation-paused');
      if (this.lipSync) this.lipSync.pause();
      if (window.speechEngine) window.speechEngine.pause();
      if (window.labEffects) window.labEffects.pauseAmbient();
      this.stopClock();
      if (this.dialogueTimeout) clearTimeout(this.dialogueTimeout);
    } else {
      // Resume
      this.isPaused = false;
      this.btnPlayPauseIcon.textContent = '⏸';
      if (this.viewportEl) this.viewportEl.classList.remove('presentation-paused');
      if (this.lipSync) this.lipSync.resume();
      if (window.speechEngine) window.speechEngine.resume();
      if (window.labEffects) window.labEffects.playAmbient();
      this.startClock();
      this.resumeStep();
    }
  }

  restartPresentation() {
    this.stopClock();
    if (this.dialogueTimeout) clearTimeout(this.dialogueTimeout);
    if (this.lipSync) this.lipSync.resetAll();
    if (this.gestures) this.gestures.resetAll();
    if (window.speechEngine) window.speechEngine.stop();
    if (window.matlabViewer) window.matlabViewer.hidePanel();
    if (this.viewportEl) this.viewportEl.classList.remove('presentation-paused');

    this.elapsedTime = 0;
    this.currentSceneIdx = 0;
    this.currentDialogueIdx = 0;
    this.updateClockUI();

    if (this.creditsEl) this.creditsEl.classList.add('hidden');
    this.startPresentation();
  }

  jumpToScene(sceneIdx) {
    if (!this.scriptData || !this.scriptData.scenes[sceneIdx]) return;
    if (this.dialogueTimeout) clearTimeout(this.dialogueTimeout);
    if (this.lipSync) this.lipSync.resetAll();
    if (this.gestures) this.gestures.resetAll();
    if (window.speechEngine) window.speechEngine.stop();

    this.currentSceneIdx = sceneIdx;
    this.currentDialogueIdx = 0;

    const totalScenes = this.scriptData.scenes.length;
    this.elapsedTime = (sceneIdx / totalScenes) * this.totalDuration;
    this.updateClockUI();

    if (this.creditsEl) this.creditsEl.classList.add('hidden');
    if (!this.isPlaying) {
      this.startPresentation();
    } else {
      this.playCurrentStep();
    }
  }

  seekToTime(targetSeconds) {
    if (!this.scriptData) return;
    this.elapsedTime = targetSeconds;
    this.updateClockUI();

    const ratio = targetSeconds / this.totalDuration;
    const targetSceneIdx = Math.min(
      this.scriptData.scenes.length - 1,
      Math.floor(ratio * this.scriptData.scenes.length)
    );
    this.jumpToScene(targetSceneIdx);
  }

  startClock() {
    this.stopClock();
    this.timerInterval = setInterval(() => {
      if (!this.isPaused && this.isPlaying) {
        this.elapsedTime += 1;
        this.updateClockUI();
        if (this.elapsedTime >= this.totalDuration) {
          this.endPresentation();
        }
      }
    }, 1000);
  }

  stopClock() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  updateClockUI() {
    this.formatTime(this.elapsedTime, this.timeCurrent);
    const pct = Math.min(100, (this.elapsedTime / this.totalDuration) * 100);
    if (this.timelineFill) {
      this.timelineFill.style.width = `${pct}%`;
    }
  }

  formatTime(seconds, element) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    const text = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    if (element) element.textContent = text;
    return text;
  }

  playCurrentStep() {
    if (!this.scriptData) return;
    const scene = this.scriptData.scenes[this.currentSceneIdx];
    if (!scene) {
      this.endPresentation();
      return;
    }

    // Update scene camera & visual overlays
    this.updateSceneVisuals(scene);

    const dialogue = scene.dialogues[this.currentDialogueIdx];
    if (!dialogue) {
      // Advance to next scene
      this.currentSceneIdx += 1;
      this.currentDialogueIdx = 0;
      if (this.currentSceneIdx < this.scriptData.scenes.length) {
        this.playCurrentStep();
      } else {
        this.endPresentation();
      }
      return;
    }

    // Execute dialogue line
    this.executeDialogue(dialogue, scene);
  }

  resumeStep() {
    const scene = this.scriptData.scenes[this.currentSceneIdx];
    if (!scene) return;
    const dialogue = scene.dialogues[this.currentDialogueIdx];
    if (!dialogue) return;

    const stepDuration = dialogue.duration || 10;
    this.dialogueTimeout = setTimeout(() => {
      this.advanceDialogue();
    }, stepDuration * 1000);
  }

  updateSceneVisuals(scene) {
    // 1. Camera class on background
    if (this.bgLayer) {
      this.bgLayer.className = `viewport-layer ${scene.camera || 'cam-default'}`;
    }

    // 2. Scene dropdown sync
    if (this.sceneDropdown) {
      this.sceneDropdown.value = (this.currentSceneIdx + 1).toString();
    }
    if (this.sceneBadge) {
      this.sceneBadge.textContent = `Scene ${scene.id}: ${scene.name}`;
    }

    // 3. Holographic HUD toggles
    document.querySelectorAll('.scene-hud-panel').forEach(p => p.classList.add('hidden'));
    if (scene.active_hud && scene.active_hud !== 'general' && scene.active_hud !== 'matlab') {
      const hudEl = document.getElementById(`hud-${scene.active_hud}`);
      if (hudEl) hudEl.classList.remove('hidden');
    }

    // 4. MATLAB Scientific Panel Trigger (Scene 4)
    if (scene.is_scientific_demo) {
      if (window.matlabViewer) window.matlabViewer.showPanel();
    } else {
      if (window.matlabViewer) window.matlabViewer.hidePanel();
    }
  }

  executeDialogue(dialogue, scene) {
    const isSenior = (dialogue.speaker === 'senior');
    const speakerData = this.scriptData.characters[dialogue.speaker];
    const durationSec = dialogue.duration || 10;

    // 1. Highlight active character slot
    if (isSenior) {
      this.charSenior.className = 'character-slot active-speaker';
      this.charJunior.className = 'character-slot listening';
      this.speakerDot.style.background = 'var(--cyan-neon)';
      this.speakerDot.style.boxShadow = '0 0 8px var(--cyan-neon)';
      this.speakerName.style.color = 'var(--cyan-neon)';
    } else {
      this.charJunior.className = 'character-slot active-speaker';
      this.charSenior.className = 'character-slot listening';
      this.speakerDot.style.background = 'var(--purple-neon)';
      this.speakerDot.style.boxShadow = '0 0 8px var(--purple-neon)';
      this.speakerName.style.color = '#d69eff';
    }

    // 2. Update subtitle labels and text
    this.speakerName.textContent = speakerData ? speakerData.name : dialogue.speaker;
    this.speakerRole.textContent = speakerData ? speakerData.role : '';
    this.subtitlesContent.textContent = dialogue.text;

    // 3. Trigger Natural Hand and Arm Gestures
    if (this.gestures) {
      this.gestures.trigger(dialogue.speaker, dialogue.gesture, durationSec);
    }

    // 4. Start Real-Time Phoneme Lip-Sync
    if (this.lipSync) {
      this.lipSync.start(dialogue.speaker, dialogue.text, durationSec);
    }

    // 5. Connect to Speech Playback
    const onSpeechStart = () => {
      // Speech started
    };

    const onSpeechEnd = () => {
      if (this.lipSync) this.lipSync.stop();
    };

    const onSpeechBoundary = (e) => {
      if (this.lipSync) this.lipSync.onWordBoundary(e);
    };

    if (window.speechEngine) {
      window.speechEngine.speak(
        dialogue.text,
        dialogue.speaker,
        onSpeechStart,
        onSpeechEnd,
        onSpeechBoundary
      );
    }

    // Duration timer to advance next line
    this.dialogueTimeout = setTimeout(() => {
      this.advanceDialogue();
    }, durationSec * 1000);
  }

  advanceDialogue() {
    if (this.lipSync) this.lipSync.stop();
    this.currentDialogueIdx += 1;
    this.playCurrentStep();
  }

  endPresentation() {
    this.isPlaying = false;
    this.stopClock();
    if (this.lipSync) this.lipSync.resetAll();
    if (this.gestures) this.gestures.resetAll();
    if (window.speechEngine) window.speechEngine.stop();
    if (window.matlabViewer) window.matlabViewer.hidePanel();

    // Reset characters
    this.charSenior.className = 'character-slot listening';
    this.charJunior.className = 'character-slot listening';

    // Show Credits Slate
    if (this.creditsEl) {
      this.creditsEl.classList.remove('hidden');
    }

    if (window.labEffects) {
      window.labEffects.playChime();
    }
    console.log('[APP] Presentation completed successfully.');
  }

  toggleSubtitles() {
    if (!this.subtitlesBar) return;
    this.subtitlesBar.classList.toggle('hidden-subtitles');
    this.btnSubtitles.classList.toggle('active');
  }

  toggleAudio() {
    if (!window.speechEngine) return;
    const isMuted = window.speechEngine.toggleMute();
    this.btnAudio.classList.toggle('active', !isMuted);
    this.btnAudioIcon.textContent = isMuted ? '🔇' : '🔊';

    if (isMuted && window.labEffects) {
      window.labEffects.pauseAmbient();
    } else if (window.labEffects) {
      window.labEffects.playAmbient();
    }
  }
}

function initPresentationApp() {
  if (!window.presentationApp) {
    window.presentationApp = new PresentationApp();
  }
}

if (document.readyState === 'loading' && !document.getElementById('presentation-viewport')) {
  document.addEventListener('DOMContentLoaded', initPresentationApp);
} else {
  initPresentationApp();
}
