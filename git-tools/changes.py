import copy
import json
import requests
import os
from distutils.version import LooseVersion

# CONFIG -----------------------

output = "/tmp/CHANGES.rst"
repo = "bird-house/birdhouse-deploy"

# avoid rate-limiting
oauth_token = ""

# ------------------------------

headers = {}
if oauth_token:
    headers["Authorization"] = "token {}".format(oauth_token)

tags_url = "https://api.github.com/repos/{}/tags".format(repo)
tag_base = "https://github.com/{}/tree/".format(repo)

tmp_tags = "/tmp/tags.json"
tmp_info = "/tmp/info.json"

tags = []
if os.path.isfile(tmp_tags):
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
if os.path.isfile(tmp_info):
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
    if message_lines[0].startswith("Merge pull request"):
        message_lines = message_lines[2:]
    message_lines[0] = "- " + message_lines[0]
    if len(message_lines) > 1:
        message_lines[1:] = ["  " + m for m in message_lines[1:]]
    change_lines.extend(version_lines + message_lines + [""])


with open(output, "w") as changes_file:
    changes_file.writelines(line + "\n" for line in change_lines)
