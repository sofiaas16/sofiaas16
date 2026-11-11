// Run: node tests/game.test.js
const assert = require("assert");
const { createGame } = require("../game.js");

let seed = 1;
const rng = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
let n = 0;
const test = (name, fn) => { fn(); n++; console.log("✓", name); };

test("starts ready with 3 segments and food on a free cell", () => {
  const g = createGame({ rng });
  const s = g.state;
  assert.equal(s.status, "ready");
  assert.equal(s.snake.length, 3);
  assert.ok(s.food);
  assert.ok(!s.snake.some((p) => p.x === s.food.x && p.y === s.food.y));
});

test("step does nothing until started", () => {
  const g = createGame({ rng });
  const head = { ...g.state.snake[0] };
  g.step();
  assert.deepEqual(g.state.snake[0], head);
});

test("moves right and cannot reverse into itself", () => {
  const g = createGame({ rng });
  g.start();
  const x = g.state.snake[0].x;
  assert.equal(g.setDirection("left"), false);
  g.step();
  assert.equal(g.state.snake[0].x, x + 1);
});

test("queues quick turns (up then left) without dying", () => {
  const g = createGame({ rng });
  g.start();
  assert.ok(g.setDirection("up"));
  assert.ok(g.setDirection("left"));
  g.step(); g.step();
  assert.equal(g.state.status, "running");
  assert.equal(g.state.dir, "left");
});

test("eating grows the snake, scores and speeds up", () => {
  const g = createGame({ rng });
  const s = g.state;
  s.food = { x: s.snake[0].x + 1, y: s.snake[0].y, type: "heart", born: 0 };
  const len = s.snake.length, speed = s.tickMs;
  g.start(); g.step();
  assert.equal(g.state.snake.length, len + 1);
  assert.equal(g.state.score, 1);
  assert.ok(g.state.tickMs < speed);
  assert.equal(g.state.lastEvent.type, "eat");
});

test("stars are worth 3", () => {
  const g = createGame({ rng });
  const s = g.state;
  s.food = { x: s.snake[0].x + 1, y: s.snake[0].y, type: "star", born: 0 };
  g.start(); g.step();
  assert.equal(g.state.score, 3);
});

test("hitting a wall ends the game", () => {
  const g = createGame({ rng, cols: 6, rows: 6 });
  g.state.food = { x: 0, y: 0, type: "heart", born: 0 };
  g.start();
  for (let i = 0; i < 10 && g.state.status === "running"; i++) g.step();
  assert.equal(g.state.status, "over");
});

test("biting itself ends the game", () => {
  const g = createGame({ rng });
  const s = g.state;
  s.snake = [{ x: 5, y: 5 }, { x: 4, y: 5 }, { x: 4, y: 6 }, { x: 5, y: 6 }, { x: 6, y: 6 }, { x: 7, y: 6 }, { x: 8, y: 6 }];
  s.dir = "up"; s.food = { x: 0, y: 0, type: "heart", born: 0 };
  g.start();
  g.setDirection("right"); g.step(); // (6,5)
  g.setDirection("down"); g.step();  // (6,6) is body -> dead
  assert.equal(g.state.status, "over");
});

test("moving into the tail cell is allowed (tail moves away)", () => {
  const g = createGame({ rng });
  const s = g.state;
  s.snake = [{ x: 5, y: 5 }, { x: 5, y: 6 }, { x: 6, y: 6 }, { x: 6, y: 5 }];
  s.dir = "up"; s.food = { x: 0, y: 0, type: "heart", born: 0 };
  g.start(); g.setDirection("right"); g.step();
  assert.equal(g.state.status, "running");
});

test("unpicked star turns back into a heart", () => {
  const g = createGame({ rng, cols: 80, rows: 5 });
  g.state.snake = [{ x: 2, y: 2 }, { x: 1, y: 2 }, { x: 0, y: 2 }];
  g.state.food = { x: 70, y: 0, type: "star", born: 0 };
  g.start();
  let expired = false;
  for (let i = 0; i < 60 && !expired; i++) { g.step(); expired = !!(g.state.lastEvent && g.state.lastEvent.type === "expire"); }
  assert.ok(expired);
  assert.equal(g.state.food.type, "heart");
});

test("pause stops movement", () => {
  const g = createGame({ rng });
  g.start(); g.togglePause();
  const head = { ...g.state.snake[0] };
  g.step();
  assert.deepEqual(g.state.snake[0], head);
  assert.equal(g.togglePause(), "running");
});

test("filling the board wins", () => {
  const g = createGame({ rng, cols: 3, rows: 1 });
  const s = g.state;
  s.snake = [{ x: 1, y: 0 }, { x: 0, y: 0 }];
  s.food = { x: 2, y: 0, type: "heart", born: 0 };
  g.start(); g.step();
  assert.equal(g.state.status, "won");
});

console.log(`\n${n} tests passed`);
