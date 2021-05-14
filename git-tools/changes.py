"""
Generates a CHANGES.rst file from an history of Github semantic versioning tags.

The commit contents where the tag versions were placed are used to generate the
content under each version section inside the changes.

"""
__version__ = "0.1.0"
# above are used to generate the CLI description

import argparse
import copy
import json
import requests
import os
from distutils.version import LooseVersion


def generate_changes(repo, output, oauth_token=None, cache=True):

    if os.path.isdir(output) or not output.endswith(".rst"):
        output = os.path.join(output, "CHANGES.rst")

    out_dir = os.path.abspath(os.path.dirname(output))
    os.makedirs(out_dir, exist_ok=True)

    headers = {}
    if oauth_token:
        headers["Authorization"] = "token {}".format(oauth_token)

    tags_url = "https://api.github.com/repos/{}/tags".format(repo)
    cache_dir = "/tmp/{}".format(repo.replace("/", "_"))
    tmp_tags = "{}/tags.json".format(cache_dir)
    tmp_info = "{}/info.json".format(cache_dir)
    if cache:
        os.makedirs(cache_dir, exist_ok=True)

    tags = []
    if cache and os.path.isfile(tmp_tags):
        with open(tmp_tags) as tmp_file:
            tags = json.load(tmp_file)
    else:
        page = 0
        while True:
            tags_resp = requests.get(tags_url + "?per_page=100&page={}".format(page), headers=headers)
            tags_list = tags_resp.json()
            if tags_resp.status_code != 200 or not tags_list:
                break
            tags.extend(tags_list)
            page += 1
        if tags:
            with open(tmp_tags, "w") as tmp_file:
                json.dump(tags, tmp_file)

    print("Total tags:", len(tags))

    tags = {t["name"]: t for t in tags}

    tag_messages = []
    if cache and os.path.isfile(tmp_info):
        with open(tmp_info) as tmp_file:
            tag_messages = json.load(tmp_file)
    else:
        for tag, info in reversed(sorted(tags.items(), key=lambda t: LooseVersion(t[0]))):
            commit_url = info["commit"]["url"]
            commit = requests.get(commit_url, headers=headers).json()
            message = commit["commit"]["message"]
            date = commit["commit"]["committer"]["date"].split("T")[0]
            tag_messages.append({"tag": tag, "message": message, "date": date})
        if tag_messages:
            with open(tmp_info, "w") as tmp_file:
                json.dump(tag_messages, tmp_file)

    if not tag_messages:
        raise ValueError("Missing tag information!")

    separator_line = "=" * 120
    change_lines = [
        ".. :changelog:",
        "",
        "Changes",
        "*******",
        "",
        ".. **DEFINE LATEST CHANGES UNDER BELOW 'Unreleased' SECTION - THEY WILL BE INTEGRATED IN NEXT RELEASE**",
        "",
        "`Unreleased <https://github.com/{}/tree/master>`_ (latest)".format(repo),
        separator_line,
        "",
        "- <changes here> ...",
        "",
    ]

    new_version_lines = [
        "`{{tag}} <https://github.com/{}/tree/{{tag}}>`_ ({{date}})".format(repo),
        separator_line,
        "",
    ]

    for tag_info in tag_messages:
        version_lines = copy.deepcopy(new_version_lines)
        version_lines[0] = version_lines[0].format(**tag_info)
        message_lines = tag_info["message"].splitlines()
        if message_lines[0].startswith("Merge pull request"):   # auto message by github
            message_lines = message_lines[2:]                   # +1 line spacing
        message_lines[0] = "- " + message_lines[0]
        if len(message_lines) > 1:
            message_lines[1:] = ["  " + m for m in message_lines[1:]]
        change_lines.extend(version_lines + message_lines + [""])

    with open(output, "w") as changes_file:
        changes_file.writelines(line + "\n" for line in change_lines)
    print("Output generated: {}".format(output))


def main():
    ap = argparse.ArgumentParser(prog="changes", description=__doc__, add_help=True)
    ap.add_argument("repo", help="Repository [organization/repository] to employ for fetching tags.")
    ap.add_argument("--output", "-o", default="CHANGES.rst", help="Output location of CHANGES.rst file.")
    ap.add_argument("--token", "-t",
                    help="OAuth Token to use to access the repository. "
                         "This can be used both for private repository access, but also to "
                         "increase rate-limit range to avoid access problems when calling the script too often.")
    ap.add_argument("--no-cache", action="store_false", dest="cache",
                    help="Disable caching of intermediate request results between executions. "
                         "Caching avoids quickly reaching request rate-limit that blocks access to metadata.")
    ap.add_argument("--version", "-v", action="version", version="%(prog)s {}".format(__version__))
    args = ap.parse_args()
    generate_changes(args.repo, args.output, args.token, args.cache)


if __name__ == "__main__":
    main()
