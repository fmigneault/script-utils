import os
import sys
CUR_DIR = os.path.realpath(os.path.dirname(__file__))
ROOT_DIR = os.path.realpath(os.path.join(CUR_DIR, ".."))

CONVERT_TOOLS_DIR = os.path.join(ROOT_DIR, "convert-tools")
DOCKER_TOOLS_DIR = os.path.join(ROOT_DIR, "docker-tools")
MERGE_TOOLS_DIR = os.path.join(ROOT_DIR, "merge-tools")

sys.path.insert(0, CONVERT_TOOLS_DIR)
sys.path.insert(0, DOCKER_TOOLS_DIR)
sys.path.insert(0, MERGE_TOOLS_DIR)
