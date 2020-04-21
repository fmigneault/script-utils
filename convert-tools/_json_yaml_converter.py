#!/user/bin/env python

import argparse
import json
import os
import sys
import yaml


def read_content(file_path):
    if file_path.endswith(".json"):
        with open(file_path, 'r') as f:
            return json.load(f)
    if file_path.endswith(".yml") or file_path.endswith(".yaml"):
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def write_content(data, file_path):
    if file_path.endswith(".json"):
        with open(file_path, 'w') as f:
            json.dump(data, f)
            return True
    if file_path.endswith(".yml") or file_path.endswith(".yaml"):
        with open(file_path, 'w') as f:
            yaml.safe_dump(f, f)
            return True
    return False


def main():
    args = sys.argv[1:]
    name = os.path.splitext(os.path.split(__file__)[-1])[0]
    if len(args) > 1 and args[0] == "--name":
        name = os.path.split(args[1])[-1]
        args = args[2:]
    ap = argparse.ArgumentParser(name, description="Tool that converts JSON<=>YAML", add_help=True)
    ap.add_argument("file_in", type=str, help="Input file from where to read data to convert (JSON or YAML).")
    ap.add_argument("file_out", type=str, help="Output file where to write converted data (JSON or YAML).")
    args = ap.parse_args(args=args)
    if not args.file_in or not os.path.isfile(args.file_in):
        raise IOError("cannot reading: [{}]".format(args.file_in))
    data = read_content(args.file_in)
    success = write_content(data, args.file_out)
    if not success or not args.file_out or not os.path.isfile(args.file_out):
        raise IOError("failed writing: [{}]".format(args.file_out))


if __name__ == "__main__":
    main()
