/* Pastel Snake — rendering, input and UI. Logic lives in game.js */
(function () {
  "use strict";

  const COLS = 17;
  const ROWS = 17;
  const game = SnakeCore.createGame({ cols: COLS, rows: ROWS });

  const $ = (id) => document.getElementById(id);
  const canvas = $("board");
  const ctx = canvas.getContext("2d");
  const scoreEl = $("score");
  const bestEl = $("best");
  const overlay = $("overlay");
  const ovKicker = $("ov-kicker");
  const ovTitle = $("ov-title");
  const ovText = $("ov-text");
  const ovBtn = $("ov-btn");
  const pauseBtn = $("pause");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const darkMode = window.matchMedia("(prefers-color-scheme: dark)");

  // ── best score (storage can be unavailable: private mode, sandboxed iframes…)
  const BEST_KEY = "pastel-snake-best";
  let best = 0;
  try { best = parseInt(localStorage.getItem(BEST_KEY), 10) || 0; } catch (e) { /* ignore */ }
  bestEl.textContent = best;
  function saveBest(v) {
    best = v;
    bestEl.textContent = v;
    try { localStorage.setItem(BEST_KEY, String(v)); } catch (e) { /* ignore */ }
  }

  // ── palette
  function palette() {
    const dark = darkMode.matches;
    return {
      board: dark ? "#1C2640" : "#EEF6FF",
      board2: dark ? "#202B47" : "#E3EFFC",
      body: ["#F8BBD0", "#EFB6D6", "#E3B4DC", "#D6B4E0", "#CDB4DB", "#BFC0EA", "#B5CBF4", "#A9D3FF"],
      head: dark ? "#F8BBD0" : "#E58FB4",
      eye: "#293247",
      heart: dark ? "#F8BBD0" : "#E37BA8",
      star: dark ? "#A2D2FF" : "#5E9DE0",
      shine: "#FFFFFF",
      text: dark ? "#F4F1F8" : "#293247",
    };
  }

  // ── canvas sizing (crisp on retina)
  let cell = 20;
  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 3);
    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);
    cell = canvas.width / COLS;
    draw();
  }
  window.addEventListener("resize", resize);

  // ── particles (sparkles when eating)
  let particles = [];
  function burst(at, color) {
    if (reduceMotion.matches) return;
    for (let i = 0; i < 12; i++) {
      const a = (Math.PI * 2 * i) / 12 + Math.random() * 0.4;
      const sp = 0.06 + Math.random() * 0.08;
      particles.push({ x: at.x + 0.5, y: at.y + 0.5, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, life: 1, color });
    }
  }
  let floaters = [];

  // ── drawing helpers
  function roundRect(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  const HEART = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."];
  function pixelHeart(cx, cy, size, color) {
    const p = size / 7;
    const ox = cx - size / 2;
    const oy = cy - (p * 6) / 2;
    ctx.fillStyle = color;
    HEART.forEach((row, r) =>
      [...row].forEach((ch, c) => { if (ch === "X") ctx.fillRect(ox + c * p, oy + r * p, Math.ceil(p), Math.ceil(p)); })
    );
    ctx.fillStyle = "rgba(255,255,255,.85)";
    ctx.fillRect(ox + 1 * p, oy + 1 * p, Math.ceil(p), Math.ceil(p));
  }
  function sparkle(cx, cy, r, color) {
    const k = r * 0.3;
    ctx.beginPath();
    ctx.moveTo(cx, cy - r);
    ctx.quadraticCurveTo(cx + k, cy - k, cx + r, cy);
    ctx.quadraticCurveTo(cx + k, cy + k, cx, cy + r);
    ctx.quadraticCurveTo(cx - k, cy + k, cx - r, cy);
    ctx.quadraticCurveTo(cx - k, cy - k, cx, cy - r);
    ctx.fillStyle = color;
    ctx.fill();
  }

  let t0 = performance.now();
  function draw(now) {
    now = now || performance.now();
    const s = game.state;
    const pal = palette();
    const W = canvas.width;
    ctx.clearRect(0, 0, W, W);
    // checkerboard
    for (let y = 0; y < ROWS; y++)
      for (let x = 0; x < COLS; x++) {
        ctx.fillStyle = (x + y) % 2 ? pal.board2 : pal.board;
        ctx.fillRect(x * cell, y * cell, cell + 0.5, cell + 0.5);
      }

    // food
    if (s.food) {
      const pulse = reduceMotion.matches ? 1 : 1 + Math.sin((now - t0) / 220) * 0.08;
      const cx = (s.food.x + 0.5) * cell;
      const cy = (s.food.y + 0.5) * cell;
      if (s.food.type === "star") {
        const age = s.ticks - s.food.born;
        const fading = age > 35 && Math.floor(now / 150) % 2 === 0;
        if (!fading) sparkle(cx, cy, cell * 0.46 * pulse, pal.star);
      } else {
        pixelHeart(cx, cy, cell * 0.78 * pulse, pal.heart);
      }
    }

    // snake (tail first so the head is on top)
    const n = s.snake.length;
    for (let i = n - 1; i >= 0; i--) {
      const p = s.snake[i];
      const inset = i === 0 ? cell * 0.06 : cell * 0.12;
      ctx.fillStyle = i === 0 ? pal.head : pal.body[Math.min(pal.body.length - 1, Math.floor((i / Math.max(n - 1, 1)) * (pal.body.length - 1)))];
      roundRect(p.x * cell + inset, p.y * cell + inset, cell - inset * 2, cell - inset * 2, cell * 0.28);
      ctx.fill();
    }
    // head details
    const h = s.snake[0];
    const d = SnakeCore.DIRS[s.dir];
    const hx = (h.x + 0.5) * cell;
    const hy = (h.y + 0.5) * cell;
    const px = -d.y; // perpendicular
    const py = d.x;
    ctx.fillStyle = pal.eye;
    const dead = s.status === "over";
    [-1, 1].forEach((side) => {
      const ex = hx + d.x * cell * 0.14 + px * side * cell * 0.2;
      const ey = hy + d.y * cell * 0.14 + py * side * cell * 0.2;
      if (dead) {
        ctx.fillRect(ex - cell * 0.09, ey - cell * 0.02, cell * 0.18, cell * 0.05);
      } else {
        ctx.fillRect(ex - cell * 0.06, ey - cell * 0.06, cell * 0.12, cell * 0.12);
      }
    });
    // blush
    ctx.fillStyle = "rgba(255,255,255,.45)";
    ctx.fillRect(hx - d.x * cell * 0.18 - cell * 0.05, hy - d.y * cell * 0.18 - cell * 0.05, cell * 0.1, cell * 0.1);

    // particles & floating "+n"
    particles.forEach((q) => {
      ctx.globalAlpha = Math.max(q.life, 0);
      sparkle(q.x * cell, q.y * cell, cell * 0.12, q.color);
    });
    ctx.globalAlpha = 1;
    floaters.forEach((f) => {
      ctx.globalAlpha = Math.max(f.life, 0);
      ctx.fillStyle = pal.text;
      ctx.font = `700 ${Math.round(cell * 0.6)}px ui-monospace, Menlo, Consolas, monospace`;
      ctx.textAlign = "center";
      ctx.fillText(f.text, (f.x + 0.5) * cell, (f.y + 0.1 - (1 - f.life) * 1.2) * cell);
    });
    ctx.globalAlpha = 1;
  }

  // ── overlay
  function showOverlay(kind) {
    const s = game.state;
    overlay.classList.remove("hidden");
    if (kind === "ready") {
      ovKicker.textContent = "ready?";
      ovTitle.textContent = "Collect the hearts";
      ovText.textContent = "Use the arrow keys, WASD or swipe. Stars are worth 3 points, but they don't wait forever.";
      ovBtn.textContent = "▶ Play";
    } else if (kind === "paused") {
      ovKicker.textContent = "paused";
      ovTitle.textContent = "Little break ☕";
      ovText.textContent = "Press Space or the button to keep playing.";
      ovBtn.textContent = "▶ Resume";
    } else if (kind === "over" || kind === "won") {
      const record = s.score > 0 && s.score >= best;
      ovKicker.textContent = kind === "won" ? "you filled the board!" : record ? "new best score ✦" : "game over";
      ovTitle.textContent = `${s.score} point${s.score === 1 ? "" : "s"}`;
      ovText.textContent = kind === "won" ? "That's every single cell. Legendary." : "Every bug is just a chance to try again.";
      ovBtn.textContent = "↻ Play again";
    }
    ovBtn.focus({ preventScroll: true });
  }
  function hideOverlay() { overlay.classList.add("hidden"); }

  function restart() {
    game.reset();
    particles = [];
    floaters = [];
    scoreEl.textContent = "0";
    acc = 0;
    showOverlay("ready");
    draw();
  }

  function primaryAction() {
    const st = game.state.status;
    if (st === "over" || st === "won") { restart(); return; }
    if (st === "ready" || st === "paused") { game.start(); hideOverlay(); }
  }
  ovBtn.addEventListener("click", primaryAction);
  $("restart").addEventListener("click", restart);
  pauseBtn.addEventListener("click", () => togglePause());

  function togglePause() {
    const st = game.state.status;
    if (st === "ready") return primaryAction();
    const now = game.togglePause();
    if (now === "paused") showOverlay("paused");
    else if (now === "running") hideOverlay();
    pauseBtn.textContent = now === "paused" ? "▶" : "❚❚";
    pauseBtn.setAttribute("aria-label", now === "paused" ? "Resume" : "Pause");
  }

  function turn(dir) {
    const st = game.state.status;
    if (st === "over" || st === "won") return;
    if (st === "paused") {
      game.togglePause();
      pauseBtn.textContent = "❚❚";
      pauseBtn.setAttribute("aria-label", "Pause");
    }
    game.setDirection(dir);
    if (game.state.status === "ready") game.start();
    if (game.state.status === "running") hideOverlay();
  }

  // ── keyboard
  const KEYS = {
    ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right",
    w: "up", s: "down", a: "left", d: "right", W: "up", S: "down", A: "left", D: "right",
  };
  window.addEventListener("keydown", (e) => {
    if (KEYS[e.key]) { e.preventDefault(); turn(KEYS[e.key]); return; }
    if (e.key === " " || e.key === "p" || e.key === "P") { e.preventDefault(); togglePause(); return; }
    if (e.key === "Enter" || e.key === "r" || e.key === "R") {
      if (document.activeElement && document.activeElement.tagName === "BUTTON" && e.key === "Enter") return;
      e.preventDefault();
      const st = game.state.status;
      if (st === "over" || st === "won" || e.key !== "Enter") restart(); else primaryAction();
    }
  });

  // ── touch: swipe on the board
  let touchStart = null;
  canvas.addEventListener("touchstart", (e) => {
    const t = e.changedTouches[0];
    touchStart = { x: t.clientX, y: t.clientY };
    e.preventDefault();
  }, { passive: false });
  canvas.addEventListener("touchmove", (e) => {
    if (!touchStart) return;
    const t = e.changedTouches[0];
    const dx = t.clientX - touchStart.x;
    const dy = t.clientY - touchStart.y;
    if (Math.max(Math.abs(dx), Math.abs(dy)) > 24) {
      turn(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "right" : "left") : dy > 0 ? "down" : "up");
      touchStart = { x: t.clientX, y: t.clientY };
    }
    e.preventDefault();
  }, { passive: false });
  canvas.addEventListener("touchend", () => { touchStart = null; });

  // ── on-screen pad
  document.querySelectorAll(".key").forEach((btn) => {
    const go = (e) => { e.preventDefault(); turn(btn.dataset.dir); btn.classList.add("on"); setTimeout(() => btn.classList.remove("on"), 120); };
    btn.addEventListener("pointerdown", go);
    btn.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") go(e); });
  });

  // pause automatically when the tab is hidden
  document.addEventListener("visibilitychange", () => {
    if (document.hidden && game.state.status === "running") togglePause();
  });

  // ── loop
  let last = performance.now();
  let acc = 0;
  function frame(now) {
    const dt = Math.min(now - last, 250);
    last = now;
    const s = game.state;
    if (s.status === "running") {
      acc += dt;
      while (acc >= s.tickMs && game.state.status === "running") {
        acc -= s.tickMs;
        game.step();
        const ev = game.state.lastEvent;
        if (ev && ev.type === "eat") {
          scoreEl.textContent = game.state.score;
          burst(ev.at, ev.food === "star" ? "#A2D2FF" : "#F8BBD0");
          floaters.push({ x: ev.at.x, y: ev.at.y, text: "+" + ev.points, life: 1 });
          if (navigator.vibrate && !reduceMotion.matches) { try { navigator.vibrate(8); } catch (e) { /* ignore */ } }
        }
        if (game.state.status === "over" || game.state.status === "won") {
          if (game.state.score > best) saveBest(game.state.score);
          scoreEl.textContent = game.state.score;
          setTimeout(() => showOverlay(game.state.status), 380);
        }
      }
    } else {
      acc = 0;
    }
    particles.forEach((q) => { q.x += q.vx; q.y += q.vy; q.life -= 0.04; });
    particles = particles.filter((q) => q.life > 0);
    floaters.forEach((f) => { f.life -= 0.025; });
    floaters = floaters.filter((f) => f.life > 0);
    draw(now);
    requestAnimationFrame(frame);
  }

  resize();
  showOverlay("ready");
  requestAnimationFrame(frame);
})();
