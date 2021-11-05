#!/usr/bin/env python3

"""rrdclean - tool to remove spikes from rrd files"""

# based on rrdclean by Magnus Hagander <magnus@hagander.net>
# https://github.com/mhagander/rrdclean

# TODO: refactor remove_spikes() and add unit tests

import argparse
import os
import re
import subprocess
import sys
import tempfile
import xml.dom.minidom


UNIT_MAP = {}
UNIT_MAP["K"] = 10 ** 3
UNIT_MAP["M"] = 10 ** 6
UNIT_MAP["G"] = 10 ** 9
UNIT_MAP["T"] = 10 ** 12
UNIT_MAP["P"] = 10 ** 15
UNIT_MAP["E"] = 10 ** 18


def remove_spikes(rrd_file: str, cutoff: float):
    """Remove spikes from rrd file."""
    updates = []

    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="rrd-orig-", delete=False
    ) as f:
        xml_file = f.name

    print("Dumping to temp file: {}".format(xml_file))

    result = subprocess.run("rrdtool dump {} {}".format(rrd_file, xml_file), shell=True)

    if result.returncode != 0:  # TODO: use check=True and try/except
        print("Error dumping")
        sys.exit(1)

    try:
        with open(xml_file) as f:
            data = f.read()
    except FileNotFoundError:
        print("{} not found".format(xml_file))
        sys.exit(1)

    dom = xml.dom.minidom.parseString(data)
    for row in dom.getElementsByTagName("row"):
        # row: <!-- 2021-10-28 21:45:00 CDT / 1635475500 --> <row><v>9.9554738243e+06</v><v>9.9554470127e+06</v></row>
        # let's look at the parts of a row
        # <!-- 2021-10-28 21:45:00 CDT / 1635475500 -->: previousSibling.previousSibling.nodeValue
        # <row>: beginning of row
        # <v>: beginning of child node 0
        # 9.9554738243e+06: value of child node 0's firstChild
        # </v>
        # <v>: beginning of child node 1
        # 9.9554470127e+06: value of child node 1's firstChild
        # </v>
        # </row>
        update = [row.previousSibling.previousSibling.nodeValue]
        is_spike = False
        for child in row.childNodes:
            if (
                child.firstChild.nodeValue != "NaN"
                and float(child.firstChild.nodeValue) > cutoff
            ):
                update.append(child.firstChild.nodeValue)
                update.append("NaN")
                child.firstChild.nodeValue = "NaN"  # remove the spike
                is_spike = True
            else:
                update.append(child.firstChild.nodeValue)
                update.append(child.firstChild.nodeValue)
        if is_spike:
            updates.append(update)

    if updates:
        print("Spikes found:")
        for update in updates:
            print(update)

        response = input("Remove them [y/N]? ")
        if response.lower() == "y":
            dump_file(dom, rrd_file)
        else:
            print("Not modifying file.  Goodbye.")
            return

    else:
        print("No spikes found")
        return


def dump_file(dom, rrd_file: str):
    """Now dump the output."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="rrd-clean-", delete=False
    ) as f:
        xml_file = f.name

    try:
        with open(xml_file, "w") as f:
            dom.writexml(f)
    except FileNotFoundError:
        print("{} not found".format(xml_file))
        sys.exit(1)

    rrd_bak = "{}.bak".format(rrd_file)

    os.rename(rrd_file, rrd_bak)

    result = subprocess.run(
        "rrdtool restore -r {} {}".format(xml_file, rrd_file), shell=True
    )

    if result.returncode != 0:  # TODO: use check=True and try/except
        print("Error restoring")
        sys.exit(1)


def normalize_threshold(thold: str) -> int:
    """Normalize the threshold (e.g. turn 10k into 10000).  Return -1 on error."""
    try:
        ret = int(thold)
        return ret
    except ValueError:
        pass

    match = re.match(r"(\d+(?:\.\d+)?)([kmgt])", thold, flags=re.IGNORECASE)
    if not match:
        return -1

    return float(match.group(1)) * UNIT_MAP[match.group(2).upper()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove spikes from an RRD file")
    parser.add_argument("file", type=str, help="RRD file (binary format)")
    parser.add_argument(
        "threshold", type=str, help="Spike threshold (may use M, G, T units)"
    )
    args = parser.parse_args()

    src = args.file
    threshold = normalize_threshold(args.threshold)

    if not os.path.exists(src):
        print("File {} does not exist".format(src))
        sys.exit(1)

    if threshold == -1:
        print("Invalid threshold {}".format(args.threshold))
        sys.exit(1)

    print(threshold)
    remove_spikes(src, threshold)
