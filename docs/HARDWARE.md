# Hardware

## Adapter
- **DSD TECH SH-C31G**: galvanically isolated USB-to-CAN-FD adapter, based on
  the CANable 2.0 Pro design, FD up to 5 Mbit/s, open-source hardware
  (CERN-OHL-S-2.0) (inferred: confirm against the unit and its docs)
- Termination: on-board 120 Ω jumper. **OFF on the car.** The vehicle bus is
  already terminated.

## Host
- Jetson Orin Nano, Ubuntu / L4T, native SocketCAN
- Kernel: `6.8.12-1021-tegra`.
- The stock L4T kernel did not ship `gs_usb`. It is an **out-of-tree, unsigned build**
  installed at `/lib/modules/6.8.12-1021-tegra/updates/gs_usb.ko` (taints the kernel).
  **Rebuild it after any kernel update**, or the adapter won't enumerate.
- Interfaces: `can0` = on-board mttcan (unused). `can1` = the USB adapter (gs_usb).

## Firmware
- **candleLight** (`gs_usb` driver): native SocketCAN, shows up as `canN`. Plan of record.
- Shipped firmware: **candleLight**, USB ID `1d50:606f` (verified 2026-11-16).
- gs_usb reports `FD` in `ctrlmode_supported`, so CAN-FD should not need slcan.
  Not needed day one (see decision 002). (inferred: FD not exercised)
- `listen-only on` is honored: `ip -details` shows `<LISTEN-ONLY>` (verified 2026-11-16).
- Quirk: the TX error counter is not reset by `ip link set down/up`; a stale
  value (e.g. 128) can persist. Replug the adapter to clear it.

## Wiring (OBD-II J1962)
| OBD pin | Signal  | Adapter |
|---------|---------|---------|
| 6       | CAN-H   | CANH    |
| 14      | CAN-L   | CANL    |
| 4 or 5  | GND     | GND (inferred: decide whether to share ground across the isolation barrier) |

Via a flying-lead pigtail. Check pinout continuity with a meter before
connecting.

## Bus limits
- The OBD port sits behind the **CEM gateway**. Expect diagnostic + UDS
  traffic, not the full internal broadcast. (inferred: the first baseline
  capture will show how much passive traffic there is)
- UDS writes are gated by seed-key (service `0x27`). Out of scope; see the TX ban in CLAUDE.md.
