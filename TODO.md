# TODO

_Inbox and Backlog items are not approved for implementation._

## Inbox

## Backlog
- [ ] Build a DBC from decoded signals
- [ ] Live dashboard / logger
- [ ] Scrubbed sample captures (VIN removed) under `samples/` for the repo

## Ready
- [ ] Button-press frame diffing (baseline vs. single action)

## Now
- [ ] Baseline capture: parked, engine off, termination OFF, listen-only (`can1`)

## Done Recently
- [x] Bench test on the Orin: candleLight, `can1`, listen-only honored, bench log VALID; real listen-only fixture; tests fixed for Python 3.12; scripts default to `can1` (2026-11-16)
- [x] `scripts/log_baseline.py` written + unit tests (17 pass on macOS), untested on hardware (2026-11-14)
- [x] Project docs set up, git repo pushed (2026-11-13)
- [x] `.gitignore` keeps raw captures local (2026-11-13)
- [x] `scripts/setup_can.sh` written: listen-only enforced, untested (2026-11-13)
