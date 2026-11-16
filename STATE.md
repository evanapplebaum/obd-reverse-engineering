# State

_Snapshot, overwritten each session. Last updated: 2026-11-16._

## Objective
Capture a clean baseline on the car: parked, engine off, listen-only.

## Working capabilities
Bench-verified on the Orin, 2026-11-16 (no car, termination ON):
- Adapter enumerates as `can1` (gs_usb, candleLight `1d50:606f`). `can0` is on-board mttcan.
- `sudo scripts/setup_can.sh` brings `can1` up at 500k with `<LISTEN-ONLY>` read back.
- `scripts/log_baseline.py --label bench --duration 10`: 0 frames, 0 errors, VALID,
  LISTEN-ONLY at start and end.
- Both scripts now default to `can1`.

## Work in progress
None.

## Blockers
None.

## Next action
At the car: parked, engine off, **termination jumper OFF**, pinout checked with a meter.
`sudo scripts/setup_can.sh` → confirm `<LISTEN-ONLY>` → plug into OBD →
`scripts/log_baseline.py --label engine-off --duration 60`.

## Smallest relevant file set
- CLAUDE.md
- scripts/setup_can.sh
- scripts/log_baseline.py
- docs/HARDWARE.md
- .claude/rules/can-safety.md

## Last verification
`python3 -m unittest discover tests`: 17 pass (2026-11-16, Orin, Python 3.12.3).
Bench run of both scripts on `can1` passed (2026-11-16).

## Incident note (2026-11-16, bench only)
Before this session's bench test, a session outside this project built gs_usb and ran
`ip link set can1 up` **without** `listen-only on`. `can1` sat in normal mode with
1 TX frame counted and TX error counter 128. It was never connected to the car.
It was taken down and re-brought up with `setup_can.sh`. The TX error counter
stayed at 128 after that (see HARDWARE.md quirk).

## Open questions
- [x] Shipped firmware: candleLight (`1d50:606f`).
- [x] Interface name: `can1` (mttcan owns `can0`).
- [x] gs_usb honors `listen-only on`: yes.
- [x] iproute2 `-json` works; active mode is under `linkinfo.info_data.ctrlmode`.
- [ ] Ground: share GND across the isolation barrier or not?
- [ ] How much passive traffic shows up on OBD pins 6/14 behind the CEM gateway?
- [ ] No real `ip -json` fixture for listen-only off yet (would need normal mode on the bench).
