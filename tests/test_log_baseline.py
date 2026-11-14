"""Tests for scripts/log_baseline.py. Run: python3 -m unittest discover tests

No hardware needed. Fixtures in tests/fixtures/ are hand-written (inferred)
until replaced with real `ip -json -details` output from the Jetson.
"""
import importlib.util
import re
import struct
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIX = REPO / "tests" / "fixtures"

spec = importlib.util.spec_from_file_location("log_baseline", REPO / "scripts" / "log_baseline.py")
lb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lb)


def link(name):
    return lb.parse_link((FIX / name).read_text(), "can0")


def classic(can_id, data=b"", length=None):
    length = len(data) if length is None else length
    return struct.pack("=IB3x8s", can_id, length, data.ljust(8, b"\0"))


class LinkChecks(unittest.TestCase):
    def test_listen_only_ok(self):
        self.assertEqual(lb.link_problems(link("ip_listen_only.json"), "gs_usb", 500000), [])

    def test_normal_mode_refused_even_though_supported(self):
        # ctrlmode_supported lists LISTEN-ONLY; the active ctrlmode does not.
        l = link("ip_normal_mode.json")
        self.assertEqual(l["ctrlmode"], [])
        probs = lb.link_problems(l, "gs_usb", 500000)
        self.assertTrue(any("LISTEN-ONLY" in p for p in probs), probs)

    def test_wrong_bitrate_refused(self):
        probs = lb.link_problems(link("ip_wrong_bitrate.json"), "gs_usb", 500000)
        self.assertTrue(any("bitrate" in p for p in probs), probs)

    def test_down_refused(self):
        probs = lb.link_problems(link("ip_down.json"), "gs_usb", 500000)
        self.assertIn("interface is down", probs)

    def test_mttcan_refused(self):
        probs = lb.link_problems(link("ip_listen_only.json"), "mttcan", 500000)
        self.assertTrue(any("gs_usb" in p for p in probs), probs)

    def test_no_driver_refused(self):
        probs = lb.link_problems(link("ip_listen_only.json"), None, 500000)
        self.assertTrue(any("unknown" in p for p in probs), probs)

    def test_missing_iface(self):
        with self.assertRaises(ValueError):
            lb.parse_link((FIX / "ip_listen_only.json").read_text(), "can1")


class FrameFormat(unittest.TestCase):
    def test_standard(self):
        f = lb.format_frame(1.5, "can0", classic(0x7E8, bytes.fromhex("024100")))
        self.assertEqual(f.line, "(1.500000) can0 7E8#024100")
        self.assertEqual((f.ident, f.kind), ("7E8", "data"))

    def test_extended(self):
        f = lb.format_frame(0, "can0", classic(0x18DAF110 | lb.CAN_EFF_FLAG, b"\x01"))
        self.assertEqual(f.line, "(0.000000) can0 18DAF110#01")

    def test_empty_data(self):
        self.assertTrue(lb.format_frame(0, "can0", classic(0x100)).line.endswith("100#"))

    def test_rtr(self):
        self.assertTrue(lb.format_frame(0, "can0", classic(0x123 | lb.CAN_RTR_FLAG)).line.endswith("123#R"))
        f = lb.format_frame(0, "can0", classic(0x123 | lb.CAN_RTR_FLAG, length=2))
        self.assertTrue(f.line.endswith("123#R2"))
        self.assertEqual(f.kind, "rtr")

    def test_error(self):
        f = lb.format_frame(0, "can0", classic(lb.CAN_ERR_FLAG | 0x4, bytes(8)))
        self.assertEqual(f.line, "(0.000000) can0 20000004#0000000000000000")
        self.assertEqual(f.kind, "error")

    def test_fd(self):
        data = bytes(range(12))
        raw = struct.pack("=IBBBB64s", 0x123, 12, 0x1, 0, 0, data)
        f = lb.format_frame(0, "can0", raw)
        self.assertEqual(f.line, "(0.000000) can0 123##1" + data.hex().upper())
        self.assertEqual(f.kind, "fd")

    def test_bad_size(self):
        with self.assertRaises(ValueError):
            lb.format_frame(0, "can0", b"\0" * 10)


class NoTransmitPath(unittest.TestCase):
    """Guards .claude/rules/can-safety.md: nothing in scripts/ may transmit."""

    BANNED_TOOLS = ["cansend", "cangen", "canplayer", "cansequence",
                    "canfdtest", "cangw", "isotpsend", "isotptun"]
    SOCKET_WRITE = re.compile(r"\.send(all|to|msg|file)?\s*\(|\bos\.write\s*\(")

    def scripts(self):
        files = [p for p in (REPO / "scripts").iterdir() if p.is_file() and p.name != ".gitkeep"]
        self.assertTrue(files)
        return files

    def test_no_banned_tools(self):
        for p in self.scripts():
            text = p.read_text()
            for tool in self.BANNED_TOOLS:
                self.assertNotRegex(text, rf"\b{tool}\b", f"{p.name} mentions {tool}")

    def test_no_socket_writes(self):
        for p in self.scripts():
            self.assertIsNone(self.SOCKET_WRITE.search(p.read_text()), f"{p.name} has a write call")

    def test_python_only_runs_ip(self):
        for p in (REPO / "scripts").glob("*.py"):
            cmds = re.findall(r"subprocess\.\w+\(\s*\[\s*\"([^\"]+)\"", p.read_text())
            self.assertTrue(all(c == "ip" for c in cmds), f"{p.name} runs {cmds}")


if __name__ == "__main__":
    unittest.main()
