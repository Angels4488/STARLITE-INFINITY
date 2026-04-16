#!/usr/bin/env python3
"""
spectacular_firework_v3.py
The Grand Finale Edition.
- Supports massive particle counts (1000+ fireworks).
- Procedural Audio Synthesis via 'sox' (Linux/Ubuntu).
- Enhanced Color Palette.
- Non-blocking audio threads.
"""
from __future__ import annotations
import argparse
import json
import logging
import math
import os
import random
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

# -------------------------
# Logging
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("spectacular_firework_v3")

# -------------------------
# Defaults and constants
# -------------------------
DEFAULT_MODEL = "gemini-2.5-flash-preview-09-2025"
DEFAULT_DURATION = 30  # Increased duration for the grand finale
DEFAULT_FIREWORKS = 100 # Bumped up default
# Massive palette for "All Colors"
COLOR_PALETTE = [
    "bright_red", "red", "bright_yellow", "yellow", "gold1",
    "bright_cyan", "cyan", "turquoise2",
    "bright_magenta", "magenta", "hot_pink",
    "bright_green", "green", "spring_green1",
    "bright_white", "white", "wheat1",
    "bright_blue", "blue", "dodger_blue1",
    "orange1", "dark_orange", "purple"
]
GRAVITY = 0.05
DRAG = 0.99

# -------------------------
# Utilities
# -------------------------
def getenv(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)

def clamp(v: float, a: float, b: float) -> float:
    return max(a, min(b, v))

# -------------------------
# Sound Engine (Procedural)
# -------------------------
class SoundEngine:
    """
    Generates procedural explosion sounds using 'play' (sox) or system bell.
    Runs in threads to prevent blocking the animation.
    """
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.has_sox = False
        if self.enabled:
            # Check for sox
            try:
                subprocess.run(["play", "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.has_sox = True
            except FileNotFoundError:
                logger.warning("'sox' not found. Falling back to system bell for sound. (Install: sudo apt install sox)")

    def play_explosion(self, intensity: float):
        if not self.enabled:
            return

        def _sound_thread():
            if self.has_sox:
                # Synth command: randomized pitch decay
                # play -n synth [len] saw [freq] fade 0 [len] [len]
                duration = random.uniform(0.1, 0.3)
                start_freq = random.uniform(200, 800)
                end_freq = start_freq * 0.5
                vol = clamp(intensity, 0.1, 1.0)
                # Fire and forget subprocess
                try:
                    subprocess.run(
                        ["play", "-q", "-n", "synth", str(duration), "saw", f"{start_freq}-{end_freq}", "vol", str(vol)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception:
                    pass
            else:
                # Fallback to bell
                print('\a', end='', flush=True)

        # Only spawn a thread for sound if we aren't overwhelming the system
        if threading.active_count() < 50:
            t = threading.Thread(target=_sound_thread, daemon=True)
            t.start()

# -------------------------
# Message provider
# -------------------------
def fetch_remote_message(api_key: str, api_url: str, model: str, timeout: float = 2.0) -> Optional[str]:
    if not api_key or not api_url:
        return None
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "prompt": "Hype New Year shoutout! One short sentence.", "max_tokens": 40}
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            if "message" in data and isinstance(data["message"], str): return data["message"].strip()
            if "output" in data and isinstance(data["output"], str): return data["output"].strip()
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                first = data["choices"][0]
                if isinstance(first, dict):
                    text = first.get("text") or first.get("message") or first.get("content")
                    if isinstance(text, str): return text.strip()
        return str(data)[:200]
    except Exception as exc:
        return None

def choose_message(seed: Optional[int]) -> str:
    env_msg = getenv("GEMINI_MESSAGE")
    if env_msg: return env_msg
    api_key = getenv("GEMINI_API_KEY")
    api_url = getenv("GEMINI_API_URL")
    if api_key and api_url:
        msg = fetch_remote_message(api_key, api_url, DEFAULT_MODEL)
        if msg: return msg
    local = [
        "MAXIMUM OVERDRIVE! The Machine Spirit is lit! 🎆",
        "1000 SUNS! Let the code burn bright! 🔥",
        "System Limit Breaker Engaged! Happy New Year! 🚀",
        "We don't compile, we IGNITE! 💻✨"
    ]
    rng = random.Random(seed)
    return rng.choice(local)

# -------------------------
# Physics
# -------------------------
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    char: str
    color: str
    life: float
    brightness: float = 1.0

    def step(self):
        self.vx *= DRAG
        self.vy = self.vy * DRAG + GRAVITY
        self.x += self.vx
        self.y += self.vy
        self.life -= random.uniform(0.04, 0.08) # Randomized decay for organic look
        self.brightness = clamp(self.life, 0.0, 1.0)

@dataclass
class Firework:
    x: int
    y: int
    target_y: int
    vy: float
    color: str
    sound_engine: SoundEngine
    exploded: bool = False
    trail: List[Tuple[int, int]] = field(default_factory=list)
    particles: List[Particle] = field(default_factory=list)

    def ascend_step(self):
        self.y = max(self.target_y, self.y - self.vy)
        self.trail.insert(0, (self.x, int(self.y)))
        if len(self.trail) > 4: # Short trails for performance
            self.trail.pop()
        if self.y <= self.target_y:
            self.exploded = True
            self._explode()

    def _explode(self):
        # Play sound
        self.sound_engine.play_explosion(random.uniform(0.5, 1.0))

        # Particle explosion
        count = random.randint(15, 40)
        base_speed = random.uniform(0.8, 2.2)

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = base_speed * random.uniform(0.5, 1.5)
            # Polar conversion
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed * 0.8 # Flatten slightly for perspective

            char = random.choice([".", "*", "+", "x", "o"])
            life = random.uniform(1.0, 3.0)
            p = Particle(x=self.x, y=self.y, vx=vx, vy=vy, char=char, color=self.color, life=life)
            self.particles.append(p)

    def step_particles(self):
        # In-place filtering for speed
        self.particles = [p for p in self.particles if (p.step() or p.life > 0)]

# -------------------------
# Renderer
# -------------------------
class Renderer:
    def __init__(self, console: Console, width: int, height: int, sound_engine: SoundEngine, low_cpu: bool = False):
        self.console = console
        self.width = width
        self.height = height
        self.fireworks: List[Firework] = []
        self.sound_engine = sound_engine
        self.low_cpu = low_cpu

    def spawn(self, seed: Optional[int] = None):
        rng = random.Random(seed)
        x = rng.randint(self.width // 10, 9 * self.width // 10)
        y = self.height + 1
        target_y = rng.randint(self.height // 8, self.height // 2)
        vy = rng.uniform(1.0, 2.2) # Faster ascent
        color = rng.choice(COLOR_PALETTE)
        fw = Firework(x=x, y=y, target_y=target_y, vy=vy, color=color, sound_engine=self.sound_engine)
        self.fireworks.append(fw)

    def step(self):
        # Efficient list comp removal
        for fw in self.fireworks:
            if not fw.exploded:
                fw.ascend_step()
            else:
                fw.step_particles()
        self.fireworks = [fw for fw in self.fireworks if not fw.exploded or fw.particles]

    def render_panel(self) -> Panel:
        # Optimized grid construction
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        style_grid: List[List[Optional[str]]] = [[None for _ in range(self.width)] for _ in range(self.height)]

        # Draw logic (reverse order so newer stuff draws on top)
        for fw in reversed(self.fireworks):
            # Trails
            if not fw.exploded:
                for idx, (tx, ty) in enumerate(fw.trail):
                    if 0 <= tx < self.width and 0 <= ty < self.height:
                        grid[ty][tx] = "|" if idx == 0 else ":"
                        style_grid[ty][tx] = f"dim {fw.color}"
            # Particles
            else:
                for p in fw.particles:
                    sx, sy = int(p.x), int(p.y)
                    if 0 <= sx < self.width and 0 <= sy < self.height:
                        if p.brightness > 0.8:
                            st = f"bold {p.color}"
                        elif p.brightness > 0.4:
                            st = p.color
                        else:
                            st = "dim white"
                        grid[sy][sx] = p.char
                        style_grid[sy][sx] = st

        # String building
        lines = []
        for r in range(self.height):
            seg_text = Text()
            current_style = None
            buffer = ""
            for c in range(self.width):
                char = grid[r][c]
                sty = style_grid[r][c]
                if sty != current_style:
                    if buffer:
                        seg_text.append(buffer, style=current_style)
                    buffer = char
                    current_style = sty
                else:
                    buffer += char
            if buffer:
                seg_text.append(buffer, style=current_style)
            lines.append(seg_text)

        title = f"🎇 NEON CITY GRAND FINALE 🎇 | Active Shells: {len(self.fireworks)}"
        return Panel(Text("\n").join(lines), title=title, border_style="bright_yellow", style="on black")

# -------------------------
# CLI
# -------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Spectacular Firework Terminal Display V3")
    p.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION, help="Animation duration")
    p.add_argument("--count", "-n", type=int, default=DEFAULT_FIREWORKS, help="Total fireworks to launch")
    p.add_argument("--seed", type=int, default=None, help="RNG seed")
    p.add_argument("--sound", "-s", action="store_true", help="Enable procedural audio synthesis")
    p.add_argument("--export", "-e", type=str, default=None, help="Export summary JSON")
    p.add_argument("--low-cpu", action="store_true", help="Reduce FPS")
    return p.parse_args()

def main():
    args = parse_args()
    console = Console()
    width = max(50, console.size.width - 4)
    height = max(15, console.size.height - 4)

    # Init Audio
    sound_engine = SoundEngine(enabled=args.sound)
    if args.sound and not sound_engine.has_sox:
        logger.info("NOTE: 'sox' missing. Using system bell for audio.")

    message = choose_message(args.seed)
    renderer = Renderer(console, width, height, sound_engine, args.low_cpu)
    rng_master = random.Random(args.seed)

    # High Density Schedule
    spawn_times = sorted([rng_master.uniform(0, args.duration * 0.95) for _ in range(args.count)])
    spawn_index = 0
    start = time.time()

    stop = False
    def _sig(sig, frame):
        nonlocal stop
        stop = True
    signal.signal(signal.SIGINT, _sig)

    fps = 30 if not args.low_cpu else 15
    frame_time = 1.0 / fps

    with Live(renderer.render_panel(), console=console, refresh_per_second=fps, screen=True) as live:
        try:
            while True:
                now = time.time() - start

                # Multi-spawn capability for high counts
                while spawn_index < len(spawn_times) and now >= spawn_times[spawn_index]:
                    renderer.spawn(seed=rng_master.getrandbits(64))
                    spawn_index += 1

                renderer.step()
                live.update(renderer.render_panel())

                if stop or (now >= args.duration and not renderer.fireworks):
                    break
                time.sleep(frame_time * 0.8) # Slight speedup for processing overhead
        except KeyboardInterrupt:
            pass

    # Final Summary
    console.print(Panel(
        Text(f"{message}\n\nFirework Count: {args.count}", justify="center", style="bold yellow"),
        title="✨ SEQUENCE COMPLETE ✨",
        border_style="bright_cyan"
    ))

    if args.export:
        with open(args.export, "w") as f:
            json.dump({"msg": message, "count": args.count}, f)

if __name__ == "__main__":
    main()
