#!/usr/bin/env python3
import os
import time
import sqlite3
from datetime import datetime
from typing import List, Dict, Any

from flask import Flask, jsonify

# --- CONFIG ---
BASE_DIR = os.path.expanduser("~/precision_beast")
LOG_FILE = os.path.join(BASE_DIR, "mining_audit.log")
GPU_LOG_FILE = os.path.join(BASE_DIR, "mining_audit_gpu.log")
DB_FILE = "/media/agi/bitcoin_mining.db"  # adjust if yours lives elsewhere

app = Flask(__name__)

def safe_read_log(path: str, max_lines: int = 100) -> List[str]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        return [line.rstrip("")
        for line in lines[-max_lines:]]
    except Exception:
        return []

def get_runs_summary() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return {"has_db": False}

    summary = {
        "has_db": True,
        "total_runs": 0,
        "last_run": None,
    }
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM mining_runs")
        summary["total_runs"] = cur.fetchone()[0] or 0

        cur.execute(
            "SELECT id, run_label, mode, started_at, ended_at FROM mining_runs "
            "ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if row:
            rid, label, mode, started_at, ended_at = row
            summary["last_run"] = {
                "id": rid,
                "label": label,
                "mode": mode,
                "started_at": started_at,
                "ended_at": ended_at,
                "started_iso": datetime.utcfromtimestamp(started_at).isoformat()
                if started_at else None,
                "ended_iso": datetime.utcfromtimestamp(ended_at).isoformat()
                if ended_at else None,
            }
        conn.close()
    except Exception as e:
        summary["error"] = str(e)

    return summary

def parse_hashrate_from_log(lines: List[str]) -> float:
    # Placeholder: if you later print "[STATUS] Worker X: YY.YY MH/s" lines,
    # you can parse them here and compute total.
    return 0.0

@app.route("/status")
def status():
    now = datetime.utcnow().isoformat()
    logs = safe_read_log(LOG_FILE, max_lines=50)
    gpu_logs = safe_read_log(GPU_LOG_FILE, max_lines=50)
    runs = get_runs_summary()
    total_hashrate_mhs = parse_hashrate_from_log(logs)

    return jsonify({
        "timestamp_utc": now,
        "node": "PrecisionTower",
        "cpu_hashrate_mhs": total_hashrate_mhs,
        "db_summary": runs,
        "log_tail": logs,
        "gpu_log_tail": gpu_logs,
    })

@app.route("/logs")
def logs():
    return jsonify({
        "cpu": safe_read_log(LOG_FILE, max_lines=200),
        "gpu": safe_read_log(GPU_LOG_FILE, max_lines=200),
    })

@app.route("/runs")
def runs():
    return jsonify(get_runs_summary())

if __name__ == "__main__":
    port = int(os.environ.get("BEAST_STATUS_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)

