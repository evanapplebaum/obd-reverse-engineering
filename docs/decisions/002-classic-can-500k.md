# 002: Target classic CAN @ 500 kbit/s

**Status:** Accepted

## Context
The adapter supports CAN-FD, but the bus reachable at the OBD port is expected to be classic CAN.

## Decision
Target classic CAN at 500 kbit/s now. FD capability is future-proofing, not a day-one need.

## Reason
The XC40 high-speed bus at the OBD port is classic 500k. (inferred)

## Consequences
- candleLight/gs_usb is enough. No need to deal with FD firmware or kernel support yet.

## Revisit when
- The first capture shows error frames, no traffic, or FD frames at 500k.
