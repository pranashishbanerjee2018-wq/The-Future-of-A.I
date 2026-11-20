/**
 * THE FUTURE OF ARTIFICIAL INTELLIGENCE
 * Ambient Laboratory Visual Effects & Audio Controller
 * File: static/js/lab_effects.js
 */

class LabEffects {
  constructor() {
    this.canvas = document.getElementById('ambient-particles-canvas');
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.particles = [];
    this.numParticles = 45;
    this.ambientAudio = document.getElementById('audio-ambient-loop');
    this.uiChime = document.getElementById('audio-ui-chime');

    this.initCanvas();
    this.initParticles();
    this.animateParticles();
    this.initFullscreen();
  }

  initCanvas() {
    if (!this.canvas) return;
    const resize = () => {
      this.canvas.width = this.canvas.parentElement.clientWidth;
      this.canvas.height = this.canvas.parentElement.clientHeight;
    };
    resize();
    window.addEventListener('resize', resize);
  }

  initParticles() {
    if (!this.canvas) return;
    this.particles = [];
    for (let i = 0; i < this.numParticles; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        radius: Math.random() * 2 + 1,
        vx: (Math.random() - 0.5) * 0.4,
        vy: -Math.random() * 0.5 - 0.15,
        alpha: Math.random() * 0.6 + 0.2,
        color: Math.random() > 0.4 ? '#00d4ff' : '#b544fe'
      });
    }
  }

  animateParticles() {
    if (!this.ctx || !this.canvas) return;
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    for (let p of this.particles) {
      p.x += p.vx;
      p.y += p.vy;

      // Wrap around screen boundaries
      if (p.y < 0) p.y = this.canvas.height;
      if (p.x < 0) p.x = this.canvas.width;
      if (p.x > this.canvas.width) p.x = 0;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = p.color;
      this.ctx.globalAlpha = p.alpha;
      this.ctx.shadowBlur = 8;
      this.ctx.shadowColor = p.color;
      this.ctx.fill();
    }
    this.ctx.globalAlpha = 1.0;
    this.ctx.shadowBlur = 0;

    requestAnimationFrame(() => this.animateParticles());
  }

  playAmbient() {
    if (this.ambientAudio) {
      this.ambientAudio.volume = 0.22;
      this.ambientAudio.play().catch(e => {
        console.log('[EFFECTS] Audio autoplay prevented:', e);
      });
    }
  }

  pauseAmbient() {
    if (this.ambientAudio) {
      this.ambientAudio.pause();
    }
  }

  playChime() {
    if (this.uiChime) {
      this.uiChime.currentTime = 0;
      this.uiChime.volume = 0.35;
      this.uiChime.play().catch(() => {});
    }
  }

  initFullscreen() {
    const btnFs = document.getElementById('ctrl-fullscreen');
    if (!btnFs) return;
    btnFs.addEventListener('click', () => {
      const elem = document.documentElement;
      if (!document.fullscreenElement) {
        if (elem.requestFullscreen) elem.requestFullscreen();
        else if (elem.webkitRequestFullscreen) elem.webkitRequestFullscreen();
        else if (elem.msRequestFullscreen) elem.msRequestFullscreen();
      } else {
        if (document.exitFullscreen) document.exitFullscreen();
        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
        else if (document.msExitFullscreen) document.msExitFullscreen();
      }
    });
  }
}

window.labEffects = new LabEffects();
