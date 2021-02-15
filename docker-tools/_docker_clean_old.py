#!/usr/bin/env python
"""
Removes older versions of corresponding docker images according to their repository tags.
"""

__version__ = "0.1.0"

import argparse
import logging
import os
import subprocess
import sys
from distutils.version import LooseVersion
from functools import total_ordering

LOGGER = logging.getLogger("docker-clean-old")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

STATUS_REMOVE = "-"
STATUS_EXCLUDE = "e"
STATUS_INCLUDE = "i"
STATUS_FORCED = "f"
STATUS_KEEP = " "


@total_ordering
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
    them, but only that they should be considered as *less* recent than version-only equivalent. For example, following
    sorting is applied from least to most recent:

        post-0.6
        pre-0.6
        0.6

    The plain '0.6' is considered the newest version even though 'post-0.6' could suggest it was tagged after '0.6'.
    Also, 'pre-0.6' is considered newer than 'post-0.6' simply because of alphabetical order. The lexical
    interpretation of 'pre-' and 'post-', or any other variants, are completely ignored.
    The behaviour is primarily intended to keep '<version>' and '[prefix-]<version>[-suffix]' variations
    close together when sorting them for complete listing of related elements.
    """
    ver_int = None  # indicates if a 'x.y.z' version is available
    ver_num = None  # value of the 'x.y.z' if available
    ver_var_pre = None   # value of variant if present before 'x.y.z' (eg: 'test-x.y.z')
    ver_var_post = None  # value of variant if present after 'x.y.z' (eg: 'x.y.z-dev')
    latest = None   # is literal 'latest' keyword
    version = None  # version elements split by '.', with isolated '-' and other variants (eg: [1, 2, 3, '-', 'dev'])

    def parse(self, vstring):
        super(LatestVersion, self).parse(vstring)
        # if parsed element are not 'x[.y[.z]]' formatted, the first version index will be its literal string
        # otherwise, version will be a list of the corresponding numbers, with always at least one integer
        if len(self.version) > 1 and self.version[0] == 'v' and isinstance(self.version[1], int):
            self.version = self.version[1:]
        self.ver_int = self.version
        if "-" in vstring:
            at = self.version.index("-")
            pre_ver = self.version[:at]
            mid_ver = self.version[at + 1:]  # +1 to skip found '-'
            post_ver = []
            # if there was a 2nd variant, assume it is post (don't support 'pre-pre-1.2.3-post')
            if "-" in mid_ver:
                at = mid_ver.index("-")
                post_ver = mid_ver[at + 1:]
                mid_ver = mid_ver[:at]
            pre = LooseVersion(".".join(str(v) for v in pre_ver))
            # if prefix variant is actually the version itself,
            # convert back middle and post and combined post variant
            if isinstance(pre.version[0], int):
                self.ver_int = pre.version
                # rebuild from original to avoid removed '.', '-' from parsing
                # use version string + start of following variant to have more robust split
                # since parsed version middle part could be repeated or very few characters
                mid_loc = str(pre) + "-" + mid_ver[0]
                self.ver_var_post = mid_ver[0] + vstring.split(mid_loc)[-1]
            # otherwise the prefix variant is actually a prefix
            # figure out if there is any version after it
            else:
                ver = LooseVersion(".".join(str(v) for v in mid_ver))
                if isinstance(ver.version[0], int):
                    self.ver_int = ver.version
                    self.ver_var_post = post_ver
                self.ver_var_pre = pre_ver

        self.ver_num = isinstance(self.ver_int[0], int)
        # undo int() conversion to compare with other words
        self.version = [str(v) for v in self.version]  # noqa
        self.latest = self.version[0] == "latest"

    def __lt__(self, other):
        if not isinstance(other, LatestVersion):
            other = LatestVersion(other)
        # compare two numbers normally
        if self.ver_num and other.ver_num:
            # same versions but different variants
            if self.ver_int == other.ver_int:
                # first handle cases where only one of them has a variant
                if (self.ver_var_pre and not other.ver_var_pre) or (not self.ver_var_post and other.ver_var_post):
                    return True
                if (not self.ver_var_pre and other.ver_var_pre) or (self.ver_var_post and not other.ver_var_post):
                    return False
                # case when both have variants and same number, simply sort alphabetically
                # if they have the same prefix variants, fallback to post one
                if self.ver_var_pre and self.ver_var_pre != other.ver_var_pre:
                    return self.ver_var_pre < other.ver_var_pre
                elif self.ver_var_post:
                    return self.ver_var_post < other.ver_var_post
            # when no variants, only numbers
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


def resolve_amount_remove(input_images, keep_count, include_images, exclude_images, sort_method,
                          include_latest=False, ignore_repo=False,dry_run=True):
    images = {}
    order_names = (sort_method == "alpha")
    for row in input_images:
        if not row:  # avoid parsing empty lines
            continue
        img, tag = row.split(" ", 1)
        repo, raw_img = img.rsplit("/") if "/" in img else None, img
        img_tag = "{}:{}".format(img, tag)
        img_key = raw_img if ignore_repo else img
        status = None
        if img in exclude_images:
            status = STATUS_EXCLUDE
        if img_tag in exclude_images:
            status = STATUS_EXCLUDE
        if ignore_repo and raw_img in exclude_images:
            status = STATUS_EXCLUDE
        if img in include_images:
            status = STATUS_INCLUDE
        if img_tag in include_images:
            status = STATUS_INCLUDE
        if ignore_repo and raw_img in include_images:
            status = STATUS_INCLUDE
        if tag == "<none>" or img == "<none>":
            status = STATUS_FORCED
        if tag == "latest":
            if not include_latest:
                status = STATUS_EXCLUDE
        if status == STATUS_EXCLUDE and not dry_run:
            continue
        images.setdefault(img_key, [])
        images[img_key].append([status, img, LatestVersion(tag)])
    if sort_method == "date":
        sorted_images = images
    else:
        sorted_images = {}
        for key in images:
            sorted_images[key] = list(sorted(images[key], key=lambda x: x[-1]))
    if dry_run:
        LOGGER.info("Would apply following changes on images:")
        LOGGER.info(" %s: keep", STATUS_KEEP)
        LOGGER.info(" %s: remove (normal)", STATUS_REMOVE)
        LOGGER.info(" %s: remove (forced)", STATUS_FORCED)
        LOGGER.info(" %s: include", STATUS_INCLUDE)
        LOGGER.info(" %s: exclude", STATUS_EXCLUDE)
        LOGGER.info("----------------------------------------")
    remove_tags = set()
    for img_key in sorted(sorted_images) if order_names else sorted_images:
        k = 0
        for i, info in reversed(list(enumerate(sorted_images[img_key]))):
            if info[0] in [STATUS_EXCLUDE, STATUS_INCLUDE, STATUS_FORCED]:
                continue
            result = STATUS_KEEP if k < keep_count else STATUS_REMOVE
            sorted_images[img_key][i][0] = result
            k = k + 1
        for status, img, tag in sorted_images[img_key]:
            if dry_run:
                LOGGER.info("%s %s:%s", status, img, tag.vstring)
            if status in [STATUS_INCLUDE, STATUS_FORCED, STATUS_REMOVE]:
                remove_tags.add("{}:{}".format(img, tag.vstring))
    return remove_tags


def docker_clean_old(keep_count=1, include_latest=True, sort_method="alpha", dry_run=False,
                     exclude_images=None, include_images=None, ignore_repo=False):
    include_images = include_images or []
    exclude_images = exclude_images or []
    cmd_img = "docker images --format '{{.Repository}} {{.Tag}}'"   # already sorted by newest to oldest creation
    LOGGER.debug("Full listing command: [%s]".format(cmd_img))
    proc = subprocess.Popen(cmd_img, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    output = output.split("\n")
    remove_tags = resolve_amount_remove(output, keep_count, sort_method=sort_method, dry_run=dry_run,
                                        include_images=include_images, exclude_images=exclude_images,
                                        include_latest=include_latest, ignore_repo=ignore_repo)
    if dry_run:
        LOGGER.debug("All done (dry-run).")
        return
    images_to_rm = ["'{}'".format(img_tag) for img_tag in remove_tags]  # ensure separation with quotes
    LOGGER.debug("List to remove:\n%s", "\n".join(images_to_rm))
    cmd_rmi = "docker rmi {}".format(" ".join(images_to_rm))
    LOGGER.debug("Full remove command: [%s]".format(cmd_rmi))
    proc = subprocess.Popen(cmd_rmi, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline, ''):  # forward stdout if command to console
        sys.stdout.write(line)  # noqa
    LOGGER.debug("Done.")


def parse():
    args = sys.argv[1:]
    name = os.path.splitext(os.path.split(__file__)[-1])[0]
    if len(args) > 1 and args[0] == "--name":
        name = os.path.split(args[1])[-1]
        args = args[2:]
    ap = argparse.ArgumentParser(name, description=__doc__, add_help=True)
    ap.add_argument("--version", "-v", action="version", version="%(prog)s {}".format(__version__))
    ap.add_argument("--sort", "-s", type=str, choices=["alpha", "date", "version"], default="alpha", dest="sort_method",
                    help="Sort method of images (only applicable for result preview with '--dry'). "
                         "With 'date', image creation date will be employed, which makes any other name possible. "
                         "With 'version', matched image names are sorted by semantic version string, but groups of "
                         "corresponding image names will not necessarily be sorted themselves. "
                         "With 'alpha', complete sorting of names followed by versions is accomplished. "
                         "Matching image groups by tag names depend on '--ignore-repo' option.")
    ap.add_argument("--keep", "-k", type=int, default=1, dest="keep_count",
                    help="Number of latest corresponding image tags to preserve.")
    ap.add_argument("--latest", "-l", action="store_true", dest="include_latest",
                    help="Include 'latest' tag as one of the N images to preserve, otherwise ignore it completely. "
                         "Tag 'latest' is always placed as most recent if using semantic version string.")
    ap.add_argument("--ignore-repo", "-r", action="store_true", dest="ignore_repo",
                    help="Match images together regardless of their repository prefix. "
                         "For example, 'my-repo/my-image:1.0' will be matched with plain 'my-image:1.0' tag. "
                         "This applies for both latest version resolution and include/exclude matching.")
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
