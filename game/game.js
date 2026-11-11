/*
 * Pastel Snake — game core (no DOM).
 * Pure logic so it can be unit-tested with Node: `node tests/game.test.js`.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SnakeCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const DIRS = {
    up: { x: 0, y: -1 },
    down: { x: 0, y: 1 },
    left: { x: -1, y: 0 },
    right: { x: 1, y: 0 },
  };
  const OPPOSITE = { up: "down", down: "up", left: "right", right: "left" };

  const START_SPEED = 150; // ms per tick
  const MIN_SPEED = 72;
  const SPEED_STEP = 4;
  const STAR_CHANCE = 0.2; // chance that a new food is a bonus star
  const STAR_LIFETIME = 45; // ticks before an uneaten star turns back into a heart

  function createGame(options) {
    const opts = Object.assign({ cols: 17, rows: 17, rng: Math.random }, options);
    const { cols, rows, rng } = opts;
    let state;

    function reset() {
      const cy = Math.floor(rows / 2);
      const cx = Math.floor(cols / 2) - 2;
      state = {
        cols,
        rows,
        snake: [
          { x: cx, y: cy },
          { x: cx - 1, y: cy },
          { x: cx - 2, y: cy },
        ],
        dir: "right",
        queue: [],
        food: null,
        score: 0,
        eaten: 0,
        tickMs: START_SPEED,
        status: "ready", // ready | running | paused | over | won
        ticks: 0,
        lastEvent: null, // { type: 'eat'|'die'|'win'|'expire', at: {x,y}, points }
      };
      placeFood();
      return state;
    }

    function freeCells() {
      const taken = new Set(state.snake.map((p) => p.x + "," + p.y));
      const out = [];
      for (let y = 0; y < rows; y++)
        for (let x = 0; x < cols; x++) if (!taken.has(x + "," + y)) out.push({ x, y });
      return out;
    }

    function placeFood(forceType) {
      const free = freeCells();
      if (free.length === 0) {
        state.food = null;
        return false;
      }
      const cell = free[Math.floor(rng() * free.length)];
      const type = forceType || (state.eaten > 0 && rng() < STAR_CHANCE ? "star" : "heart");
      state.food = { x: cell.x, y: cell.y, type, born: state.ticks };
      return true;
    }

    function setDirection(name) {
      if (!DIRS[name]) return false;
      if (state.status === "over" || state.status === "won") return false;
      const last = state.queue.length ? state.queue[state.queue.length - 1] : state.dir;
      if (name === last || name === OPPOSITE[last]) return false;
      if (state.queue.length >= 3) return false;
      state.queue.push(name);
      if (state.status === "ready") state.status = "running";
      return true;
    }

    function start() {
      if (state.status === "ready" || state.status === "paused") state.status = "running";
    }

    function togglePause() {
      if (state.status === "running") state.status = "paused";
      else if (state.status === "paused") state.status = "running";
      return state.status;
    }

    function step() {
      state.lastEvent = null;
      if (state.status !== "running") return state;
      state.ticks++;
      if (state.queue.length) state.dir = state.queue.shift();
      const d = DIRS[state.dir];
      const head = state.snake[0];
      const next = { x: head.x + d.x, y: head.y + d.y };

      // walls
      if (next.x < 0 || next.y < 0 || next.x >= cols || next.y >= rows) {
        state.status = "over";
        state.lastEvent = { type: "die", at: head };
        return state;
      }
      const eats = state.food && next.x === state.food.x && next.y === state.food.y;
      // self: the tail cell is free this tick unless we are growing
      const body = eats ? state.snake : state.snake.slice(0, -1);
      if (body.some((p) => p.x === next.x && p.y === next.y)) {
        state.status = "over";
        state.lastEvent = { type: "die", at: next };
        return state;
      }

      state.snake.unshift(next);
      if (eats) {
        const points = state.food.type === "star" ? 3 : 1;
        state.score += points;
        state.eaten++;
        state.tickMs = Math.max(MIN_SPEED, state.tickMs - SPEED_STEP);
        state.lastEvent = { type: "eat", at: next, points, food: state.food.type };
        if (!placeFood()) {
          state.status = "won";
          state.lastEvent = { type: "win", at: next, points };
        }
      } else {
        state.snake.pop();
        if (state.food && state.food.type === "star" && state.ticks - state.food.born > STAR_LIFETIME) {
          const at = { x: state.food.x, y: state.food.y };
          placeFood("heart");
          state.lastEvent = { type: "expire", at };
        }
      }
      return state;
    }

    reset();
    return {
      get state() {
        return state;
      },
      reset,
      step,
      start,
      setDirection,
      togglePause,
    };
  }

  return { createGame, DIRS, OPPOSITE, START_SPEED, MIN_SPEED };
});
