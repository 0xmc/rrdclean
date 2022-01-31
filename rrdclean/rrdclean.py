"""rrdclean - rrdclean functions."""


import os
import re
import subprocess
import sys
import tempfile
import xml.dom.minidom


UNIT_MAP = {}
UNIT_MAP["K"] = 10**3
UNIT_MAP["M"] = 10**6
UNIT_MAP["G"] = 10**9
UNIT_MAP["T"] = 10**12
UNIT_MAP["P"] = 10**15
UNIT_MAP["E"] = 10**18


def remove_spikes(rrd_file: str, threshold: float):
    """Remove spikes from rrd file."""
    updates = []

    try:
        xml_file = dump_xml(rrd_file)
    except subprocess.CalledProcessError:
        print("Error dumping")
        sys.exit(1)

    try:
        with open(xml_file, encoding="UTF-8") as f:  # type: ignore
            data = f.read()
    except FileNotFoundError:
        print(f"{xml_file} not found")
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
                and float(child.firstChild.nodeValue) > threshold
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
            restore_rrd(dom, rrd_file)
        else:
            print("Not modifying file.  Goodbye.")
            return

    else:
        print("No spikes found")
        return


def dump_xml(rrd_file: str) -> str:
    """Dump RRD to XML.  Returns temp XML filename on success, otherwise None."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="rrd-orig-", delete=False
    ) as f:
        xml_file = f.name

    print(f"Dumping to temp file: {xml_file}")

    try:
        subprocess.run(f"rrdtool dump {rrd_file} {xml_file}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise e

    return xml_file


def restore_rrd(dom, rrd_file: str):
    """Backup original RRD file and restore cleaned XML to the RRD file."""
    with tempfile.NamedTemporaryFile(
        suffix=".xml", prefix="rrd-clean-", delete=False
    ) as f:
        xml_file = f.name

    try:
        with open(xml_file, "w", encoding="UTF-8") as f:  # type: ignore
            dom.writexml(f)
    except FileNotFoundError:
        print(f"{xml_file} not found")
        sys.exit(1)

    rrd_bak = f"{rrd_file}.bak"

    try:
        os.rename(rrd_file, rrd_bak)
    except PermissionError:
        print(f"Cannot rename {rrd_file}")
        sys.exit(1)

    try:
        subprocess.run(
            f"rrdtool restore -r {xml_file} {rrd_file}", shell=True, check=True
        )
    except subprocess.CalledProcessError:
        print("Error restoring")
        sys.exit(1)


def normalize_threshold(threshold: str) -> float:
    """Normalize the threshold (e.g. turn 10k into 10000).  Raise ValueError on error."""
    try:
        ret = float(threshold)
        return ret
    except ValueError:
        pass

    units = "".join(UNIT_MAP.keys())
    match = re.match(
        rf"(\d+(?:\.\d+)?)([{units}])",
        threshold,
        flags=re.IGNORECASE,
    )
    if not match:
        raise ValueError

    return float(match.group(1)) * UNIT_MAP[match.group(2).upper()]
