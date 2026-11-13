# Hardware

## Adapter
- **DSD TECH SH-C31G**: galvanically isolated USB-to-CAN-FD adapter, based on
  the CANable 2.0 Pro design, FD up to 5 Mbit/s, open-source hardware
  (CERN-OHL-S-2.0) (inferred: confirm against the unit and its docs)
- Termination: on-board 120 Ω jumper. **OFF on the car.** The vehicle bus is
  already terminated.

## Host
- Jetson Orin Nano, Ubuntu / L4T, native SocketCAN
- Kernel version: TBD (`uname -r`). Matters for gs_usb CAN-FD support. (inferred)

## Firmware
- **candleLight** (`gs_usb` driver): native SocketCAN, shows up as `canN`. Plan of record.
- CAN-FD frames may need **slcan** firmware or a newer kernel's gs_usb FD
  support. Not needed day one (see decision 002). (inferred)
- Shipped firmware: TBD. Check `lsusb` / `dmesg` when it arrives.

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
