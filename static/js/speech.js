/**
 * THE FUTURE OF ARTIFICIAL INTELLIGENCE
 * Speech Engine & Lip-Sync Synchronization
 * File: static/js/speech.js
 */

class SpeechEngine {
  constructor() {
    this.synth = window.speechSynthesis || null;
    this.voices = [];
    this.isMuted = false;
    this.currentUtterance = null;
    this.seniorVoice = null;
    this.juniorVoice = null;
    this.fallbackTimer = null;

    if (this.synth) {
      this.initVoices();
      if (typeof this.synth.onvoiceschanged !== 'undefined') {
        this.synth.onvoiceschanged = () => this.initVoices();
      }
    }
  }

  initVoices() {
    if (!this.synth) return;
    this.voices = this.synth.getVoices();
    if (!this.voices || this.voices.length === 0) return;

    // Search for suitable English male voices
    const enVoices = this.voices.filter(v => v && v.lang && v.lang.startsWith('en'));
    
    // Look for distinct male names (David, Mark, Guy, George, James, Male)
    const maleCandidates = enVoices.filter(v => {
      const name = v.name.toLowerCase();
      return name.includes('david') || name.includes('mark') || name.includes('guy') || 
             name.includes('george') || name.includes('james') || name.includes('male') ||
             name.includes('natural');
    });

    if (maleCandidates.length >= 2) {
      this.seniorVoice = maleCandidates[0];
      this.juniorVoice = maleCandidates[1];
    } else if (maleCandidates.length === 1) {
      this.seniorVoice = maleCandidates[0];
      this.juniorVoice = enVoices.find(v => v !== this.seniorVoice) || maleCandidates[0];
    } else {
      this.seniorVoice = enVoices[0] || this.voices[0];
      this.juniorVoice = enVoices[1] || enVoices[0] || this.voices[0];
    }

    console.log('[SPEECH ENGINE] Initialized Voices:', {
      senior: this.seniorVoice ? this.seniorVoice.name : 'Default',
      junior: this.juniorVoice ? this.juniorVoice.name : 'Default'
    });
  }

  startFallbackCadence(text, onStart, onEnd, onBoundary) {
    if (this.fallbackTimer) {
      clearInterval(this.fallbackTimer);
      this.fallbackTimer = null;
    }
    if (onStart) onStart();
    const words = text.split(/\s+/);
    const totalWords = words.length;
    const wordCadenceMs = 260; // Natural conversational tempo
    let wIdx = 0;
    let charAcc = 0;

    this.fallbackTimer = setInterval(() => {
      if (wIdx < totalWords) {
        if (onBoundary) {
          onBoundary({
            name: 'word',
            charIndex: charAcc,
            charLength: words[wIdx].length,
            word: words[wIdx]
          });
        }
        charAcc += words[wIdx].length + 1;
        wIdx++;
      } else {
        clearInterval(this.fallbackTimer);
        this.fallbackTimer = null;
        if (onEnd) onEnd();
      }
    }, wordCadenceMs);
  }

  speak(text, speakerId, onStart, onEnd, onBoundary) {
    this.stop();

    if (this.isMuted || !this.synth) {
      this.startFallbackCadence(text, onStart, onEnd, onBoundary);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    this.currentUtterance = utterance;

    // Configure distinct character acoustics
    if (speakerId === 'senior') {
      utterance.voice = this.seniorVoice;
      utterance.pitch = 0.88; // Deep, mature, calm
      utterance.rate = 0.95;  // Measured, articulate
    } else {
      utterance.voice = this.juniorVoice;
      utterance.pitch = 1.15; // Higher, youthful, energetic
      utterance.rate = 1.05;  // Analytical, enthusiastic
    }

    utterance.onstart = () => {
      if (onStart) onStart();
    };

    utterance.onboundary = (e) => {
      if (onBoundary) onBoundary(e);
    };

    utterance.onend = () => {
      this.currentUtterance = null;
      if (onEnd) onEnd();
    };

    utterance.onerror = (e) => {
      console.warn('[SPEECH ENGINE] Speech synthesis error/interrupted; using fallback cadence:', e);
      this.currentUtterance = null;
      this.startFallbackCadence(text, onStart, onEnd, onBoundary);
    };

    try {
      this.synth.speak(utterance);
    } catch (err) {
      console.error('[SPEECH ENGINE] Exception in synth.speak:', err);
      this.startFallbackCadence(text, onStart, onEnd, onBoundary);
    }
  }

  stop() {
    if (this.fallbackTimer) {
      clearInterval(this.fallbackTimer);
      this.fallbackTimer = null;
    }
    if (this.synth) {
      this.synth.cancel();
      this.currentUtterance = null;
    }
  }

  pause() {
    if (this.fallbackTimer) {
      clearInterval(this.fallbackTimer);
    }
    if (this.synth && this.synth.speaking) {
      this.synth.pause();
    }
  }

  resume() {
    if (this.synth && this.synth.paused) {
      this.synth.resume();
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    if (this.isMuted) {
      this.stop();
    }
    return this.isMuted;
  }
}

window.speechEngine = new SpeechEngine();
