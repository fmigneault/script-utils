#!/user/bin/env python

import argparse
import json
import os
import sys
import yaml

__version__ = "0.3.1"


def read_content(file_path, ignore_extension=False):
    if not ignore_extension and os.path.splitext(file_path)[-1] not in [".json", ".yaml", ".yml"]:
        return False
    with open(file_path, mode='r', encoding="utf-8") as f:
        return yaml.safe_load(f)    # can read both json/yaml


def write_content(data, file_path, file_format=None, indent=None, sort=False, ensure_ascii=False):
    if not file_format:
        file_format = os.path.splitext(file_path)[-1]
    file_format = file_format.replace(".", "", 1)
    if file_format == "json":
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent, sort_keys=sort, ensure_ascii=ensure_ascii)
            return True
    if file_format in ["yaml", "yml"]:
        with open(file_path, 'w') as f:
            yaml.safe_dump(data, f, indent=indent, sort_keys=sort, allow_unicode=not ensure_ascii)
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
    ap.add_argument("--indent", type=int, dest="indent", default=None,
                    help="Specify the indentation to apply to the output JSON or YAML.")
    ap.add_argument("--sort", action="store_true", help="Sort mapping keys for the converted file.")
    ap.add_argument("--ascii", action="store_true", help="Enforce ASCII characters instead of permitting unicode.")
    f_out = ap.add_mutually_exclusive_group()
    f_out.add_argument("--json", "-j", action="store_const", const="json", dest="file_format", default="",
                       help="Specify the desired output format as JSON. Useful when the desired extension is not JSON.")
    f_out.add_argument("--yaml", "-y", "--yml", action="store_const", const="yaml", dest="file_format", default="",
                       help="Specify the desired output format as YAML. Useful when the desired extension is not YAML.")
    args = ap.parse_args(args=args)
    if not args.file_in or not os.path.isfile(args.file_in):
        raise IOError("failed reading: [{}]".format(args.file_in))
    data = read_content(args.file_in, ignore_extension=args.ignore_extension)
    success = write_content(data, args.file_out, file_format=args.file_format,
                            indent=args.indent, sort=args.sort, ensure_ascii=args.ascii)
    if not success or not args.file_out or not os.path.isfile(args.file_out):
        raise IOError("failed writing: [{}]".format(args.file_out))


if __name__ == "__main__":
    main()
