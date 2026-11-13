# 003: Host: Jetson Orin Nano

**Status:** Accepted

## Context
Needed a capture and analysis host that can sit in the car.

## Decision
Run capture and analysis on the Jetson Orin Nano.

## Reason
Bare-metal Linux with native SocketCAN, and ML-capable hardware for on-device frame analysis.

## Alternatives
- **Pi Zero 2 W**: underpowered for on-device analysis.
- **Mac**: no native SocketCAN.

## Consequences
- The Orin's own CAN controller (mttcan) may take the `can0` name. Scripts
  should not hard-code the interface. (inferred)
- Power in the car: the Jetson needs a stable supply while parked.

## Revisit when
- L4T kernel limits (gs_usb FD, listen-only) block the work.
