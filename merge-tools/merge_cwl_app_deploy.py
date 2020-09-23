#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application that will merge a CWL Application Package into the corresponding
process deployment payload. Using this, you don't need to manage two files by hand.
"""
from collections import OrderedDict
import argparse
import os
import sys
import json
import yaml


def make_parser():
    name = os.path.splitext(os.path.split(__file__)[-1])[0]
    ap = argparse.ArgumentParser(prog=name, description=__doc__, add_help=True)
    ap.add_argument("app_package", help="Location of the CWL Application Package file.")
    ap.add_argument("process_deploy", help="Location of the process deployment file.")
    return ap


def run(app_package, process_deploy):
    with open(app_package, 'r') as f:
        app = yaml.safe_load(f)
    proc_json = True
    with open(process_deploy, 'r') as f:
        try:
            proc = json.load(f, object_pairs_hook=OrderedDict)  # noqa
        except json.decoder.JSONDecodeError:
            proc_json = False
            f.seek(0)
            proc = yaml.safe_load(f)

    proc.setdefault("executionUnit", [{}])
    if not isinstance(proc["executionUnit"], list):
        proc["executionUnit"] = []
    if not len(proc["executionUnit"]):
        proc["executionUnit"].append({})
    proc["executionUnit"][0].setdefault("unit", {})
    proc["executionUnit"][0]["unit"] = app

    with open(process_deploy, 'w', encoding="utf-8") as f:
        if proc_json:
            body = json.dumps(proc, indent=4, ensure_ascii=False)
            body = body.strip() + "\n"
            f.write(body)
        else:
            yaml.safe_dump(proc, f)


def main():
    ap = make_parser()
    args = ap.parse_args(args=None if sys.argv[1:] else ['--help'])
    return run(**vars(args))


if __name__ == "__main__":
    main()
