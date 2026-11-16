#!/usr/bin/env bash
# Bring up a gs_usb (candleLight) CAN interface in LISTEN-ONLY mode at 500 kbit/s.
# Exits non-zero, and leaves the interface DOWN, unless listen-only is confirmed.
#
# Usage: sudo scripts/setup_can.sh [iface] [bitrate]
#   iface   default: can1   (the Orin's on-board mttcan owns can0)
#   bitrate default: 500000
#
# Status: written 2026-11-13, NOT yet run on hardware. (inferred)
set -euo pipefail

IFACE="${1:-can1}"
BITRATE="${2:-500000}"

die() { echo "ERROR: $*" >&2; ip link set "$IFACE" down 2>/dev/null || true; exit 1; }

[[ $EUID -eq 0 ]] || { echo "ERROR: run with sudo" >&2; exit 1; }
[[ -e /sys/class/net/$IFACE ]] || {
  echo "ERROR: $IFACE does not exist. CAN interfaces present:" >&2
  ls /sys/class/net | grep -E '^v?can' >&2 || echo "  (none)" >&2
  exit 1
}

# Refuse anything that isn't the USB adapter, so we never configure the Orin's mttcan by mistake.
DRIVER="$(basename "$(readlink -f "/sys/class/net/$IFACE/device/driver" 2>/dev/null)" 2>/dev/null || true)"
if [[ "$DRIVER" != "gs_usb" ]]; then
  echo "ERROR: $IFACE uses driver '${DRIVER:-unknown}', expected gs_usb (candleLight)." >&2
  for n in /sys/class/net/*; do
    d="$(basename "$(readlink -f "$n/device/driver" 2>/dev/null)" 2>/dev/null || true)"
    [[ "$d" == "gs_usb" ]] && echo "  gs_usb interface found: $(basename "$n")" >&2
  done
  exit 1
fi

ip link set "$IFACE" down
# Fails with "Operation not supported" if firmware/driver can't do listen-only; set -e stops us.
ip link set "$IFACE" type can bitrate "$BITRATE" listen-only on || die "could not set listen-only on $IFACE"
ip link set "$IFACE" up

DETAILS="$(ip -details link show "$IFACE")"
grep -q 'LISTEN-ONLY' <<<"$DETAILS"        || die "LISTEN-ONLY not reported by $IFACE. Interface taken down."
grep -q "bitrate $BITRATE " <<<"$DETAILS"  || die "bitrate $BITRATE not confirmed on $IFACE. Interface taken down."

echo "OK: $IFACE up, driver gs_usb, bitrate $BITRATE, LISTEN-ONLY confirmed."
echo "Reminder: termination jumper OFF on the car (can't be checked in software)."
echo "$DETAILS"
