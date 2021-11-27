"""Threshold normalization tests."""

import unittest

from parameterized import parameterized  # type: ignore

from rrdclean.rrdclean import normalize_threshold


class TestThresholds(unittest.TestCase):
    """Threshold unit tests."""

    @parameterized.expand(
        [
            ("int", "1", 1.0),
            ("float", "2.0", 2.0),
            ("int unit", "3k", 3000.0),
            ("float unit (k)", "4.4k", 4400.0),
            ("float unit (K)", "5.5K", 5500.0),
            ("int unit (m)", "6m", 6_000_000.0),
            ("int unit (g)", "7g", 7_000_000_000.0),
            ("int unit (t)", "8t", 8_000_000_000_000.0),
            ("int unit (p)", "9p", 9_000_000_000_000_000.0),
            ("int unit (E)", "10E", 10_000_000_000_000_000_000.0),
        ]
    )
    def test_pass(self, _, test_input, expected):
        """Test valid inputs."""
        result = normalize_threshold(test_input)
        self.assertEqual(result, expected)

    @parameterized.expand(
        [
            ("garbage", "foo"),
            ("unknown unit", "3B"),
        ]
    )
    def test_fail(self, _, test_input):
        """Test invalid inputs."""
        self.assertRaises(ValueError, normalize_threshold, test_input)
