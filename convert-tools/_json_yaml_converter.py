#!/user/bin/env python

import argparse
import json
import os
import sys
import yaml

__version__ = "0.2.0"


def read_content(file_path, ignore_extension=False):
    if not ignore_extension and not os.path.splitext(file_path) in [".json", ".yaml", ".yml"]:
        return False
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)    # can read both json/yaml


def write_content(data, file_path, file_format=None):
    if not file_format:
        file_format = os.path.splitext(file_path)[-1].replace(".", "")
    if file_format == "json":
        with open(file_path, 'w') as f:
            json.dump(data, f)
            return True
    if file_format in [".yaml", ".yml"]:
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
    ap.add_argument("--version", "-v", action="version", version="%(prog)s {}".format(__version__))
    ap.add_argument("--ignore", "-i", action="store_true", dest="ignore_extension",
                    help="Ignore input file extension, try to parse as either JSON or YAML.")
    f_out = ap.add_mutually_exclusive_group()
    f_out.add_argument("--json", "-j", action="store_const", const="json", dest="file_format", default="",
                       help="Specify the desired output format as JSON. Useful when the desired extension is not JSON.")
    f_out.add_argument("--yaml", "-y", "--yml", action="store_const", const="yaml", dest="file_format", default="",
                       help="Specify the desired output format as YAML. Useful when the desired extension is not YAML.")
    args = ap.parse_args(args=args)
    if not args.file_in or not os.path.isfile(args.file_in):
        raise IOError("cannot reading: [{}]".format(args.file_in))
    data = read_content(args.file_in, ignore_extension=args.ignore_extension)
    success = write_content(data, args.file_out, file_format=args.file_format)
    if not success or not args.file_out or not os.path.isfile(args.file_out):
        raise IOError("failed writing: [{}]".format(args.file_out))


if __name__ == "__main__":
    main()
