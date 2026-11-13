# State

_Snapshot, overwritten each session. Last updated: 2026-11-13._

## Objective
Get `can0` up and capture a clean baseline.

## Working capabilities
None yet. No hardware, no scripts.

## Work in progress
Docs set up. Nothing in progress in code.

## Blockers
Adapter (DSD TECH SH-C31G) arrives Mon 2026-11-16.

## Next action
Confirm or flash candleLight → `ip link` up @ 500k, **listen-only** → `candump` baseline.

## Smallest relevant file set
- CLAUDE.md
- docs/HARDWARE.md
- .claude/rules/can-safety.md
- scripts/ (empty)

## Last verification
None. Every command and bus fact is still (inferred).

## Open questions (resolve on hardware day)
- [ ] Shipped firmware: candleLight or slcan? (`lsusb`, `dmesg`)
- [ ] Interface name: the Orin Nano has its own CAN controller (mttcan). If
      that's enabled, the USB adapter may enumerate as `can1`. (inferred)
- [ ] Does gs_usb on this L4T kernel honor `listen-only on`? (inferred)
- [ ] Ground: share GND across the isolation barrier or not?
- [ ] How much passive traffic shows up on OBD pins 6/14 behind the CEM gateway?
