# State

_Snapshot, overwritten each session. Last updated: 2026-11-14._

## Objective
Get `can0` up and capture a clean baseline.

## Working capabilities
None verified on hardware.
- `scripts/setup_can.sh`: written, passes `bash -n`.
- `scripts/log_baseline.py`: written; refuses to capture unless gs_usb + up + LISTEN-ONLY
  + bitrate (via `ip -json -details`), re-checks at the end, logs candump `-L` format.
  Unit tests pass on macOS against hand-written (inferred) fixtures.

## Work in progress
None.

## Blockers
Adapter (DSD TECH SH-C31G) arrives Mon 2026-11-16.

## Next action
On the bench (no car, termination ON): `lsusb` / `dmesg` / `ip -details link show` /
`uname -r` → confirm candleLight → `sudo scripts/setup_can.sh` → confirm LISTEN-ONLY →
`scripts/log_baseline.py --label bench --duration 10` → replace test fixtures with real
`ip -json -details` output. See TODO.md Blocked.

## Smallest relevant file set
- CLAUDE.md
- scripts/setup_can.sh
- scripts/log_baseline.py
- docs/HARDWARE.md
- .claude/rules/can-safety.md

## Last verification
`bash -n scripts/setup_can.sh` passed (2026-11-13).
`python3 -m unittest discover tests`: 17 pass (2026-11-14, macOS, no hardware).

## Open questions (resolve on hardware day)
- [ ] Shipped firmware: candleLight or slcan? (`lsusb`, `dmesg`)
- [ ] Interface name: the Orin Nano has its own CAN controller (mttcan). If
      that's enabled, the USB adapter may enumerate as `can1`. (inferred; both scripts refuse non-gs_usb interfaces)
- [ ] Does gs_usb on this L4T kernel honor `listen-only on`? (inferred; the script fails loudly if not)
- [ ] Does this iproute2 support `-json`, and is the active mode under `linkinfo.info_data.ctrlmode`? (inferred; log_baseline.py depends on it)
- [ ] Ground: share GND across the isolation barrier or not?
- [ ] How much passive traffic shows up on OBD pins 6/14 behind the CEM gateway?
