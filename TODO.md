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

## Blocked (adapter arrives Mon 2026-11-16)
- [ ] Bench test: confirm firmware, interface name, run `setup_can.sh`, termination ON, no car
  - Check the script's two unverified assumptions against real output:
    (a) the driver detection via `/sys/class/net/<if>/device/driver` resolves to `gs_usb`;
    (b) `ip -details` prints `bitrate 500000 ` with a trailing space, which the grep depends on;
    (c) `LISTEN-ONLY` appears only in the active ctrlmode, not in a supported-modes list.
  - Run `scripts/log_baseline.py --label bench --duration 10`: expect 0 frames, 0 errors, VALID.
  - Save real `ip -json -details link show dev <if>` (listen-only on, and off) over the
    hand-written fixtures in `tests/fixtures/`, then rerun the tests.
- [ ] Baseline capture: parked, engine off, termination OFF, listen-only

## Done Recently
- [x] `scripts/log_baseline.py` written + unit tests (17 pass on macOS), untested on hardware (2026-11-14)
- [x] Project docs set up, git repo pushed (2026-11-13)
- [x] `.gitignore` keeps raw captures local (2026-11-13)
- [x] `scripts/setup_can.sh` written: listen-only enforced, untested (2026-11-13)
