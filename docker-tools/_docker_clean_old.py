#!/usr/bin/env python
"""
Removes older versions of corresponding docker images according their repository tags.
"""

__version__ = "0.1.0"

import argparse
import logging
import os
import subprocess
import sys
from distutils.version import LooseVersion

LOGGER = logging.getLogger("docker-clean-old")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

STATUS_REMOVE = "-"
STATUS_EXCLUDE = "e"
STATUS_INCLUDE = "i"
STATUS_KEEP = " "


class LatestVersion(LooseVersion):
    """
    Version handler that sorts tags as follows (newest to oldest):

        latest
        0.6
        pre-0.6
        0.5
        v0.4.1
        0.4
        0.4-rc
        v0.3
        0.2
        v0.1
        unknown
        random
        other

    Prefix character 'v' is ignored to match version number following it.

    The parsing of prefix/suffix semantic version modifiers separated by '-' do not take into account the meaning of
    them, but only that they should be considers as *less* recent than version-only equivalent. For example, following
    sorting is applied:

        0.6
        pre-0.6
        post-0.6

    The plain '0.6' is considered the newest version even though 'post-0.6' could suggest it was tagged after '0.6'.
    Also, 'pre-0.6' is considered newer than 'post-0.6' simply because of alphabetical order. The meaning of 'pre-'
    and 'post-' are completely ignored.
    The behaviour is primarily intended to keep '<version>' and '[prefix-]<version>[-suffix]' variations close together.
    """
    ver_int = None
    ver_num = None
    latest = None

    def parse(self, vstring):
        super(LatestVersion, self).parse(vstring)
        if len(self.version) > 1 and self.version[0] == 'v' and isinstance(self.version[1], int):
            self.version = self.version[1:]
        self.ver_int = self.version
        if "-" in vstring:
            at = self.version.index("-")
            pre = LooseVersion(".".join(str(v) for v in self.version[:at]))
            post = LooseVersion(".".join(str(v) for v in self.version[at+1:]))
            if isinstance(pre.version[0], int):
                self.ver_int = pre.version
            elif isinstance(post.version[0], int):
                self.ver_int = post.version
        self.ver_num = isinstance(self.ver_int[0], int)
        # undo int() conversion to compare with other words
        self.version = [str(v) for v in self.version]  # noqa
        self.latest = self.version[0] == "latest"

    def __lt__(self, other):
        if not isinstance(other, LatestVersion):
            other = LatestVersion(other)
        # compare two numbers normally
        if self.ver_num and other.ver_num:
            return self.ver_int < other.ver_int
        # latest is always the newest
        # other words are always oldest
        if self.latest:
            return False
        if other.latest:
            return True
        # at least one is a word at this point (non-number)
        if self.ver_num:
            return False
        if other.ver_num:
            return True
        # both words, simple compare
        return super(LatestVersion, self).__lt__(other)


def dry_run_results(sorted_images, keep_count):
    LOGGER.info("Would apply following changes on images:")
    LOGGER.info(" %s: keep", STATUS_KEEP)
    LOGGER.info(" %s: remove", STATUS_REMOVE)
    LOGGER.info(" %s: include", STATUS_INCLUDE)
    LOGGER.info(" %s: exclude", STATUS_EXCLUDE)
    LOGGER.info("----------------------------------------")
    for img in sorted_images:
        k = 0
        for i, info in reversed(list(enumerate(sorted_images[img]))):
            if info[0] in [STATUS_EXCLUDE, STATUS_INCLUDE]:
                continue
            sorted_images[img][i][0] = STATUS_KEEP if k < keep_count else STATUS_REMOVE
            k = k + 1
        for status, tag in sorted_images[img]:
            LOGGER.info("%s %s:%s", status, img, tag.vstring)


def docker_clean_old(keep_count=1, include_latest=True, sort_method="version", dry_run=False,
                     exclude_images=None, include_images=None):
    include_images = include_images or []
    exclude_images = exclude_images or []
    cmd_img = "docker images --format '{{.Repository}} {{.Tag}}'"   # already sorted by newest to oldest creation
    proc = subprocess.Popen(cmd_img, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    output = output.split("\n")
    images = {}
    for row in output:
        if not row:  # avoid parsing empty lines
            continue
        img, tag = row.split(" ", 1)
        status = None
        if img in exclude_images:
            status = STATUS_EXCLUDE
        if "{}:{}".format(img, tag) in exclude_images:
            status = STATUS_EXCLUDE
        if img in include_images:
            status = STATUS_INCLUDE
        if "{}:{}".format(img, tag) in include_images:
            status = STATUS_INCLUDE
        if tag == "latest":
            if not include_latest:
                status = STATUS_EXCLUDE
        if status == STATUS_EXCLUDE and not dry_run:
            continue
        images.setdefault(img, [])
        images[img].append([status, LatestVersion(tag)])
    if sort_method == "date":
        sorted_images = images
    else:
        sorted_images = {}
        for img in images:
            sorted_images[img] = list(sorted(images[img], key=lambda x: x[1]))
    if dry_run:
        dry_run_results(sorted_images, keep_count)
        return
    img_all = []
    img_to_rm = []
    for img in images:
        img_all.extend(["{}:{}".format(img, tag.vstring) for _, tag in sorted_images[img]])
        img_to_rm.extend(["'{}:{}'".format(img, tag.vstring) for _, tag in sorted_images[img][:-keep_count]])
    for incl in include_images:
        if incl in img_all and incl not in img_to_rm:
            img_to_rm.append('{}'.format(incl))
    cmd_rmi = "docker rmi {}".format(" ".join(img_to_rm))
    proc = subprocess.Popen(cmd_rmi, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline, ''):  # forward stdout if command to console
        sys.stdout.write(line)  # noqa


def parse():
    args = sys.argv[1:]
    name = os.path.splitext(os.path.split(__file__)[-1])[0]
    if len(args) > 1 and args[0] == "--name":
        name = os.path.split(args[1])[-1]
        args = args[2:]
    ap = argparse.ArgumentParser(name, description=__doc__, add_help=True)
    ap.add_argument("--version", "-v", action="version", version="%(prog)s {}".format(__version__))
    ap.add_argument("--sort", "-s", type=str, choices=["date", "version"], default="version", dest="sort_method",
                    help="Sort method of images. Can be by date or by semantic version string.")
    ap.add_argument("--keep-count", "-n", type=int, default=1, dest="keep_count",
                    help="Number of latest corresponding image tags to preserve.")
    ap.add_argument("--latest", "-l", action="store_true", dest="include_latest",
                    help="Include 'latest' tag as one of the N images to preserve, otherwise ignore it completely. "
                         "Tag 'latest' is always placed as most recent if using semantic version string.")
    ap.add_argument("--dry", "--dry-run", action="store_true", dest="dry_run",
                    help=("Run in dry-run mode. "
                          "No image actually gets removed, only listing images that are kept ({}), ones that would be "
                          "removed ({}), and ones excluded ({}). Listing is sorted from oldest to newest.").format(
                        STATUS_KEEP, STATUS_REMOVE, STATUS_EXCLUDE
                    ))
    ap.add_argument("--exclude", "-e", type=str, nargs="*", dest="exclude_images",
                    help="Images to exclude from the operation, "
                         "either without tag to exclude all corresponding ones by repository, "
                         "or with a tag to exclude only that specific one.")
    ap.add_argument("--include", "-i", type=str, nargs="*", dest="include_images",
                    help="Images to include in remove operation regardless of previous rules, "
                         "either without tag to include all corresponding ones by repository, "
                         "or with a tag to include only that specific one.")
    return ap.parse_args(args=args)


if __name__ == "__main__":
    cmd_args = parse()
    docker_clean_old(**vars(cmd_args))
