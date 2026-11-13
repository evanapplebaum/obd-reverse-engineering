---
paths:
  - "scripts/**"
---
# CAN safety rules

- **Read-only on a live bus.** No TX until (a) the signal is understood, and
  (b) the user explicitly approves that specific transmission in this session.
- Scripts must open the bus in **listen-only** mode, and check that it is set
  before capturing. Abort if it isn't.
- Do not write scripts that call `cansend`, `cangen`, `canplayer`,
  `cansequence`, `canfdtest`, `cangw`, `isotpsend`, `isotptun`, or open a
  socket for writing unless they are explicitly approved. `canplayer` replays
  captures onto the bus, so it is the most likely accidental transmit.
- Termination jumper OFF on the car. Silent mode for first contact.
