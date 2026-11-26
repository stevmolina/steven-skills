#!/usr/bin/env python3
"""Run the manage-project-brain test suite (stdlib unittest, no network).

Usage: python3 run-tests.py [-v]
Equivalent: python3 -m unittest discover -s scripts/tests
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    loader = unittest.TestLoader()
    tests = os.path.join(HERE, "scripts", "tests")
    suite = loader.discover(start_dir=tests, top_level_dir=tests)
    verbosity = 2 if "-v" in sys.argv else 1
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
