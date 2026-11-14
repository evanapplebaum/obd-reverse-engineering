# State

_Snapshot, overwritten each session. Last updated: 2026-11-13._

## Objective
Get `can0` up and capture a clean baseline.

## Working capabilities
None verified. `scripts/setup_can.sh` is written and passes a syntax check, but hasn't been run on hardware.

## Work in progress
Uncommitted as of 2026-11-13 closeout: `.gitignore`, `scripts/setup_can.sh`, and
doc updates to CLAUDE.md, STATE.md and TODO.md. They must be pushed before cloning on the
Jetson. Otherwise the Jetson copy won't have the script, or the gitignore that keeps
raw captures out of git.

## Blockers
Adapter (DSD TECH SH-C31G) arrives Mon 2026-11-16.

## Next action
On the bench (no car): flash or confirm candleLight → `sudo scripts/setup_can.sh` → confirm LISTEN-ONLY.

## Smallest relevant file set
- CLAUDE.md
- scripts/setup_can.sh
- docs/HARDWARE.md
- .claude/rules/can-safety.md

## Last verification
`bash -n scripts/setup_can.sh` passed (2026-11-13). Nothing has run on hardware.

## Open questions (resolve on hardware day)
- [ ] Shipped firmware: candleLight or slcan? (`lsusb`, `dmesg`)
- [ ] Interface name: the Orin Nano has its own CAN controller (mttcan). If
      that's enabled, the USB adapter may enumerate as `can1`. (inferred; the script lists gs_usb interfaces if you guess wrong)
- [ ] Does gs_usb on this L4T kernel honor `listen-only on`? (inferred; the script fails loudly if not)
- [ ] Ground: share GND across the isolation barrier or not?
- [ ] How much passive traffic shows up on OBD pins 6/14 behind the CEM gateway?
