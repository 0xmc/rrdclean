"""Spike removal tests."""

import os
import unittest
import subprocess

# from parameterized import parameterized  # type: ignore

from rrdclean.rrdclean import dump_xml, remove_spikes

# 1401b3f15d464a798642ef80edd7223e2269065d  bits.rrd
# 970063747a13ec74e60288cd5a5e55c63b3d549b  bits.rrd.clean


class TestRRD(unittest.TestCase):
    """RRD unit tests."""

    def test_dump_xml_pass(self):
        """Test valid input."""
        xml_file = dump_xml(os.path.abspath("tests/bits.rrd"))
        with open(xml_file, encoding="UTF-8") as f:
            line = f.readline().rstrip()
        self.assertEqual(line, '<?xml version="1.0" encoding="utf-8"?>')

    def test_dump_xml_fail(self):
        """Test invalid input."""
        self.assertRaises(
            subprocess.CalledProcessError, dump_xml, "tests/does_not_exist.rrd"
        )

    def test_spike_found_pass_1(self):
        updates = remove_spikes(
            os.path.abspath("tests/bits.rrd"), 1.7 * 10**10, prompt=False, dryrun=True
        )
        self.assertEqual(len(updates), 1)

    def test_spike_found_pass_2(self):
        updates = remove_spikes(
            os.path.abspath("tests/bits2.rrd"),
            2.8 * 10**11,
            prompt=False,
            dryrun=True,
        )
        self.assertEqual(len(updates), 3)

    def test_spike_found_pass_3(self):
        updates = remove_spikes(
            os.path.abspath("tests/pkts2.rrd"),
            200 * 10**6,
            prompt=False,
            dryrun=True,
        )
        self.assertEqual(len(updates), 3)
