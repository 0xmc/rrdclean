#!/usr/bin/env python3

"""rrdclean - tool to remove spikes from RRD files."""

# based on rrdclean by Magnus Hagander <magnus@hagander.net>
# https://github.com/mhagander/rrdclean

import argparse
import os
import sys

from rrdclean.rrdclean import normalize_threshold, remove_spikes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove spikes from an RRD file")
    parser.add_argument("file", type=str, help="RRD file (binary format)")
    parser.add_argument(
        "threshold", type=str, help="Spike threshold (may use M, G, T units)"
    )
    args = parser.parse_args()

    src = args.file

    if not os.path.exists(src):
        print(f"File {src} does not exist")
        sys.exit(1)

    try:
        threshold = normalize_threshold(args.threshold)
    except ValueError:
        print(f"Invalid threshold {args.threshold}")
        sys.exit(1)

    remove_spikes(src, threshold)
