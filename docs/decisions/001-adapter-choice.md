# 001: Adapter: DSD TECH SH-C31G

**Status:** Accepted

## Context
Needed a USB-to-CAN adapter for a Jetson host, connected to a car's OBD port.

## Decision
Use the DSD TECH SH-C31G (isolated, CANable 2.0 Pro design).

## Reason
Fastest shipping, plus galvanic isolation to protect the Jetson. Costs the same as the alternatives.

## Alternatives
- **Greensen pre-built**: slow shipping, not isolated.
- **DIY STM32G431 build**: good for learning only. No time or cost advantage.

## Consequences
- Open firmware: can run candleLight (gs_usb) or slcan.
- CAN-FD capable even though it isn't needed yet (see 002).

## Revisit when
- The adapter can't do listen-only under gs_usb on L4T, or isolation causes ground or signal problems.
