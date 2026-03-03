(function () {
  'use strict';

  const DEFAULT_WPM = 10;
  const INITIAL_PAUSE_MIN = 1200;
  const INITIAL_PAUSE_MAX = 1800;
  const USER_PAUSE_MS = 2000;
  const JITTER = 0.25;

  function randFloat(min, max) {
    return min + Math.random() * (max - min);
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function wpmToCharDelay(wpm) {
    const charsPerMin = wpm * 5;
    return 60000 / charsPerMin;
  }

  class Typewriter {
    constructor(wpm) {
      this._wpm = wpm || DEFAULT_WPM;
      this._baseDelay = wpmToCharDelay(this._wpm);
      this._aborted = false;
      this._paused = false;
      this._typing = false;
      this._pauseTimeout = null;
    }

    get isTyping() {
      return this._typing;
    }

    abort() {
      this._aborted = true;
      this._paused = false;
      if (this._pauseTimeout) {
        clearTimeout(this._pauseTimeout);
        this._pauseTimeout = null;
      }
    }

    pauseForUser() {
      if (!this._typing) return;
      this._paused = true;
      if (this._pauseTimeout) clearTimeout(this._pauseTimeout);
      this._pauseTimeout = setTimeout(() => {
        this._paused = false;
        this._pauseTimeout = null;
      }, USER_PAUSE_MS);
    }

    async type(lines, insertChar, onProgress) {
      this._aborted = false;
      this._paused = false;
      this._typing = true;

      const charDelayMin = this._baseDelay * (1 - JITTER);
      const charDelayMax = this._baseDelay * (1 + JITTER);
      const lineDelayMin = this._baseDelay * 1.5;
      const lineDelayMax = this._baseDelay * 2.5;

      try {
        await sleep(randFloat(INITIAL_PAUSE_MIN, INITIAL_PAUSE_MAX));
        if (this._aborted) return false;

        for (let i = 0; i < lines.length; i++) {
          if (this._aborted) return false;

          const line = lines[i];

          for (let j = 0; j < line.length; j++) {
            if (this._aborted) return false;

            while (this._paused && !this._aborted) {
              await sleep(50);
            }
            if (this._aborted) return false;

            await insertChar(line[j]);
            if (onProgress) onProgress(i, j);
            await sleep(randFloat(charDelayMin, charDelayMax));
          }

          if (i < lines.length - 1) {
            if (this._aborted) return false;
            await insertChar('\n');
            await sleep(randFloat(lineDelayMin, lineDelayMax));
          }
        }

        return true;
      } finally {
        this._typing = false;
      }
    }
  }

  window.Typewriter = Typewriter;
})();
