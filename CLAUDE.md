# xc40-can

Read and decode the CAN bus on a 2020 Volvo XC40 T5 through an isolated USB-CAN
adapter on a Jetson. **Parked only. Never on a public road.**

> Tags: anything marked **(inferred)** is unverified. Remove the tag only after
> it has been checked on real hardware.

## Commands
- Bring up bus: `sudo scripts/setup_can.sh [iface] [bitrate]` (default can0 @ 500k,
  listen-only; refuses non-gs_usb interfaces and exits unless LISTEN-ONLY is read back)
  (written, not yet run on hardware: inferred)
- Baseline log: `scripts/log_baseline.py --label <car-state> [--iface can0] [--duration s]`
  (checks only, never configures: refuses unless gs_usb + up + LISTEN-ONLY + bitrate;
  writes `captures/<stamp>_<label>.log|.json`) (written, not yet run on hardware: inferred)
- Tests (no hardware): `python3 -m unittest discover tests`

## Architecture invariants
- Host: Jetson Orin Nano, native SocketCAN, interface `can0` (inferred: see STATE.md open questions)
- Target bus: **classic CAN @ 500 kbit/s, 11-bit IDs** (ISO 15765-4) (inferred)

## Required verification
- Before any capture, confirm the interface is in listen-only/silent mode:
  `ip -details link show can0` must show `LISTEN-ONLY`.

## Change boundaries (hard)
- **NEVER** transmit to a live bus without explicit approval in this session.
  This includes `cansend`, `cangen`, `canplayer` (log replay), `cansequence`,
  `canfdtest`, `cangw`, `isotpsend`, `isotptun`, UDS tools, and any socket write.
- The real guard is the interface: `can0` must be **listen-only** before it is
  connected to the car. A controller in normal mode ACKs frames, which counts
  as transmitting.
- The adapter's termination jumper stays **OFF** when connected to the car.
- First captures happen parked with the engine off.

## Navigation
- `STATE.md`: current objective, next action, open questions
- `TODO.md`: Now / Ready / Backlog
- `docs/HARDWARE.md`: adapter, host, wiring, bus limits
- `docs/decisions/`: numbered decision records
- `.claude/rules/`: safety rules, scoped to `scripts/`
- `captures/`: raw candump logs. **Gitignored.** They can contain the VIN, so never commit raw captures.
