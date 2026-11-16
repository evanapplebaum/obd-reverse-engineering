#!/usr/bin/env python3
"""Passive baseline capture from a listen-only gs_usb CAN interface.

Refuses to run unless the interface is already up, driven by gs_usb, in
LISTEN-ONLY mode and at the expected bitrate. Configure it first with
`sudo scripts/setup_can.sh`. This script never configures the interface and
never transmits: the CAN socket is only ever read.

Writes, under captures/ (gitignored):
  <UTC stamp>_<label>.log   candump -L format
  <UTC stamp>_<label>.json  metadata, including listen-only checks at start and end

Terminal output shows IDs and counts only, never payload bytes (VIN safety).

Usage: scripts/log_baseline.py --label engine-off [--iface can1]
           [--bitrate 500000] [--duration 60] [--notes "..."]

Exit codes: 0 valid capture, 1 pre-check failed (nothing captured),
            2 capture written but marked invalid (mode/bitrate changed).

Status: written 2026-11-14, NOT yet run on hardware. (inferred)
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import signal
import socket
import struct
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAPTURES = REPO / "captures"

# linux/can.h, linux/can/raw.h
CAN_EFF_FLAG = 0x80000000
CAN_RTR_FLAG = 0x40000000
CAN_ERR_FLAG = 0x20000000
CAN_SFF_MASK = 0x000007FF
CAN_EFF_MASK = 0x1FFFFFFF
CAN_ERR_MASK = 0x1FFFFFFF
CAN_MTU = 16
CANFD_MTU = 72
SOL_CAN_RAW = 101  # SOL_CAN_BASE (100) + CAN_RAW (1)
CAN_RAW_ERR_FILTER = 2
CAN_RAW_FD_FRAMES = 5

LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


# ---------------------------------------------------------------- link checks

def parse_link(ip_json: str, iface: str) -> dict:
    """Extract what we check from `ip -json -details link show dev <iface>`.

    Only `ctrlmode` (the active modes) is read. `ctrlmode_supported` is ignored
    on purpose: a supported mode is not an active one.
    """
    entries = json.loads(ip_json)
    entry = next((e for e in entries if e.get("ifname") == iface), None)
    if entry is None:
        raise ValueError(f"{iface} not found in ip output")
    linkinfo = entry.get("linkinfo") or {}
    info = linkinfo.get("info_data") or {}
    ctrlmode = info.get("ctrlmode") or []
    if isinstance(ctrlmode, str):
        ctrlmode = ctrlmode.split()
    return {
        "ifname": iface,
        "up": "UP" in (entry.get("flags") or []),
        "info_kind": linkinfo.get("info_kind"),
        "ctrlmode": list(ctrlmode),
        "bitrate": (info.get("bittiming") or {}).get("bitrate"),
        "state": info.get("state"),
    }


def link_problems(link: dict, driver: str | None, expected_bitrate: int) -> list[str]:
    """Return every reason not to capture. Empty list means OK."""
    problems = []
    if driver != "gs_usb":
        problems.append(f"driver is '{driver or 'unknown'}', expected gs_usb (candleLight)")
    if link["info_kind"] != "can":
        problems.append(f"link kind is '{link['info_kind']}', expected can")
    if not link["up"]:
        problems.append("interface is down")
    if "LISTEN-ONLY" not in link["ctrlmode"]:
        problems.append(f"not in LISTEN-ONLY mode (active ctrlmode: {link['ctrlmode'] or 'none'})")
    if link["bitrate"] != expected_bitrate:
        problems.append(f"bitrate is {link['bitrate']}, expected {expected_bitrate}")
    return problems


def read_link(iface: str) -> dict:
    out = subprocess.run(
        ["ip", "-json", "-details", "link", "show", "dev", iface],
        capture_output=True, text=True, check=True,
    ).stdout
    return parse_link(out, iface)


def read_driver(iface: str) -> str | None:
    path = f"/sys/class/net/{iface}/device/driver"
    if not os.path.exists(path):
        return None
    return os.path.basename(os.path.realpath(path))


def check(iface: str, bitrate: int) -> tuple[dict | None, str | None, list[str]]:
    try:
        link = read_link(iface)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
        return None, None, [f"could not read link state for {iface}: {e}"]
    driver = read_driver(iface)
    return link, driver, link_problems(link, driver, bitrate)


# ------------------------------------------------------------- frame format

@dataclass
class Frame:
    line: str   # candump -L line, no newline
    ident: str  # ID as printed (hex)
    kind: str   # data | rtr | error | fd


def format_frame(ts: float, iface: str, raw: bytes) -> Frame:
    """Format a raw can_frame / canfd_frame like `candump -L`."""
    if len(raw) == CANFD_MTU:
        can_id, length, flags = struct.unpack_from("=IBB", raw)
        data = raw[8:8 + min(length, 64)]
        fd = True
    elif len(raw) == CAN_MTU:
        can_id, length = struct.unpack_from("=IB", raw)
        data = raw[8:8 + min(length, 8)]
        flags, fd = 0, False
    else:
        raise ValueError(f"unexpected frame size {len(raw)}")

    if can_id & CAN_ERR_FLAG:
        ident, kind = f"{can_id & (CAN_ERR_MASK | CAN_ERR_FLAG):08X}", "error"
    elif can_id & CAN_EFF_FLAG:
        ident, kind = f"{can_id & CAN_EFF_MASK:08X}", "data"
    else:
        ident, kind = f"{can_id & CAN_SFF_MASK:03X}", "data"

    if fd:
        body = f"{ident}##{flags & 0xF:X}{data.hex().upper()}"
        kind = "error" if kind == "error" else "fd"
    elif can_id & CAN_RTR_FLAG and kind != "error":
        body = f"{ident}#R" + (str(length) if 0 < length <= 8 else "")
        kind = "rtr"
    else:
        body = f"{ident}#{data.hex().upper()}"
    return Frame(f"({ts:.6f}) {iface} {body}", ident, kind)


# ------------------------------------------------------------------ capture

def open_rx_socket(iface: str) -> tuple[socket.socket, bool]:
    """Raw CAN socket used for recv only. Error frames on; FD frames on if supported."""
    sock = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    sock.setsockopt(SOL_CAN_RAW, CAN_RAW_ERR_FILTER, struct.pack("=I", CAN_ERR_MASK))
    try:
        sock.setsockopt(SOL_CAN_RAW, CAN_RAW_FD_FRAMES, 1)
        fd_frames = True
    except OSError:
        fd_frames = False
    sock.bind((iface,))
    sock.settimeout(0.5)
    return sock, fd_frames


def label_arg(s: str) -> str:
    if not LABEL_RE.match(s):
        raise argparse.ArgumentTypeError("use letters, digits, - and _ (max 64 chars)")
    return s


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Passive listen-only CAN baseline capture.")
    ap.add_argument("--label", required=True, type=label_arg,
                    help="car state, e.g. engine-off, ignition-on, bench")
    ap.add_argument("--iface", default="can1")
    ap.add_argument("--bitrate", type=int, default=500000)
    ap.add_argument("--duration", type=float, default=None,
                    help="seconds; omit to run until Ctrl-C")
    ap.add_argument("--notes", default="")
    args = ap.parse_args(argv)

    if not sys.platform.startswith("linux") or not hasattr(socket, "AF_CAN"):
        print("ERROR: needs Linux SocketCAN (run on the Jetson).", file=sys.stderr)
        return 1

    start_link, start_driver, problems = check(args.iface, args.bitrate)
    if problems:
        print(f"ERROR: refusing to capture on {args.iface}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("Run: sudo scripts/setup_can.sh", args.iface, args.bitrate, file=sys.stderr)
        return 1

    CAPTURES.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = CAPTURES / f"{stamp}_{args.label}"
    log_path, meta_path = Path(f"{base}.log"), Path(f"{base}.json")

    stop = False

    def on_signal(_sig, _frm):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    counts: Counter[str] = Counter()
    kinds: Counter[str] = Counter()
    sock, fd_frames = open_rx_socket(args.iface)
    start = time.time()
    deadline = start + args.duration if args.duration else None
    print(f"Capturing on {args.iface} (listen-only, {args.bitrate}) -> {log_path.name}"
          + ("" if deadline else "  [Ctrl-C to stop]"))

    with sock, open(log_path, "x", encoding="ascii") as log:
        while not stop and (deadline is None or time.time() < deadline):
            try:
                raw = sock.recv(CANFD_MTU)
            except (socket.timeout, InterruptedError):
                continue
            frame = format_frame(time.time(), args.iface, raw)
            log.write(frame.line + "\n")
            kinds[frame.kind] += 1
            if frame.kind != "error":
                counts[frame.ident] += 1
    end = time.time()

    end_link, end_driver, end_problems = check(args.iface, args.bitrate)
    valid = not end_problems
    elapsed = end - start
    total = sum(kinds.values())

    meta = {
        "label": args.label,
        "notes": args.notes,
        "valid": valid,
        "invalid_reasons": end_problems,
        "iface": args.iface,
        "expected_bitrate": args.bitrate,
        "start": {"time": start, "link": start_link, "driver": start_driver},
        "end": {"time": end, "link": end_link, "driver": end_driver},
        "duration_s": round(elapsed, 3),
        "frames_total": total,
        "frames_by_kind": dict(kinds),
        "unique_ids": len(counts),
        "id_counts": dict(sorted(counts.items())),
        "fd_frames_enabled": fd_frames,
        "timestamp_source": "host time.time() at recv (not kernel rx timestamp)",
        "kernel": platform.release(),
        "log_file": log_path.name,
    }
    with open(meta_path, "x", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")

    rate = total / elapsed if elapsed > 0 else 0.0
    print(f"\n{'VALID' if valid else 'INVALID'}: {total} frames in {elapsed:.1f}s "
          f"({rate:.1f}/s), {len(counts)} unique IDs, "
          f"{kinds['error']} error frames, {kinds['fd']} FD frames")
    for ident, n in counts.most_common(10):
        print(f"  {ident:>8}  {n}")
    for p in end_problems:
        print(f"  ! {p}", file=sys.stderr)
    print(f"Wrote {log_path.relative_to(REPO)} and {meta_path.relative_to(REPO)}")
    return 0 if valid else 2


if __name__ == "__main__":
    sys.exit(main())
