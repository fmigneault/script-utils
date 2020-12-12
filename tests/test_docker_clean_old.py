from _docker_clean_old import docker_clean_old
import mock

# uses a massive list of predefined combisons that represent possible image tags retrieved by docker
# according to tested flags, different results are expected to process it
MOCK_DOCKER_LIST = [
    # bunch on intermediate images
    "<none>:<none>",
    "<none>:<none>",
    "<none>:<none>",
    "<none>:<none>",
    "<none>:<none>",
    # some common image names
    "devops:0.0.0",
    "devops:latest",
    "python:3.7-slim",
    "python:3.7-slim-buster",
    "python:3.7-alpine",
    "python:3.8-slim",
    "python:3.8-slim-buster",
    # various combinations of tag numbers, revisions,
    # release candiates and intermediate development naming schemes
    "pavics/twitcher:<none>",
    "pavics/twitcher:magpie-1.7.3",
    "pavics/twitcher:magpie-3.0.0",
    "pavics/twitcher:magpie-3.0.0-rc",
    "pavics/twitcher:magpie-3.1.0-rc",
    "pavics/twitcher:magpie-3.3.0-dev",
    "pavics/magpie:<none>",
    "pavics/magpie:2.0.0",
    "pavics/magpie:3.0.0",
    "pavics/magpie:3.0.0-rc",
    "pavics/magpie:3.1.0-rc",
    "pavics/magpie:3.3.0-dev",
    "pavics/magpie:latest",
    # with/without 'v' prefix ofter used for version tag
    "birdhouse/twitcher:v0.5.3",
    "birdhouse/twitcher:v0.5.4",
    "birdhouse/twitcher:0.5.3",
    "birdhouse/twitcher:0.5.4",
    # multiple valid image names, but with intermedate tags or removed references
    "video-action-recognition:<none>",
    "video-action-recognition:<none>",
    "video-action-recognition:<none>",
    "video-action-recognition:<none>",
    "video-action-recognition:<none>",
    "video-action-recognition:<none>",
    "video-action-recognition:0.3.0",
    "video-action-recognition:0.4.0",
    "video-action-recognition:0.5.0",
    "video-action-recognition:0.6.0",
    "video-action-recognition:latest",
    # with differnt non-version tags and or too specific extra variations to easily interpret
    "thelper:base",
    "thelper:geo",
    "plstcharles/thelper:v0.5.0",
    "plstcharles/thelper:v0.6.2-geo-cuda-11.1-cudnn8-devel-ubuntu18.04",
    "plstcharles/thelper:v0.6.2-geo",
    "plstcharles/thelper:v0.6.2-geo-cuda-10.0-cudnn7-devel-ubuntu16.04",
    "pytorch-cuda-tester:10.0-cudnn7-devel-ubuntu16.04",
    "pytorch-cuda-tester:11.1-cudnn8-devel-ubuntu18.04",
    "nvidia/cuda:10.1-cudnn8-devel-ubuntu18.04",
    "nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04",
    "nvidia/cuda:11.1-cudnn8-devel-ubuntu18.04",
    # minimal 1 version, 1 latest combination
    "lastools:0.1.0",
    "lastools:latest",
    # many single entries
    "unidata/thredds-docker:latest",
    "ubuntu:20.04",
    "rust:latest",
    "registry:2",
    "alpine:latest",
    "pavics/canarieapi:0.4.3",
    "continuumio/miniconda3:latest",
    "tianon/true:latest",
    "stefanprodan/mgob:0.9",
    "mongo:3.4.0",
    # various combinations of the same image name/tags with/without repository prefix
    "docker-registry.crim.ca/ogc/ogc-lidar-tb16:0.2.0",
    "docker-registry.crim.ca/ogc/ogc-lidar-tb16:latest",
    "ogc-lidar-tb16:0.2.0",
    "ogc-lidar-tb16:latest",
    "ogc-thelper-toy:0.2.1",
    "ogc-thelper-toy:latest",
    "docker-registry.crim.ca/ogc/ogc-thelper-toy:0.2.1",
    "docker-registry.crim.ca/ogc/ogc-thelper-toy:latest",
    "ogc-thelper-base:1.1.0",
    "ogc-thelper-base:latest",
    "docker-registry.crim.ca/ogc/ogc-thelper-base:1.1.0",
    "docker-registry.crim.ca/ogc/ogc-thelper-base:latest",
]


def mock_process(cmd, *_, **__):
    class MockProcess(object):
        remove = []

        @staticmethod
        def communicate(*_, **__):
            output = "\n".join(MOCK_DOCKER_LIST)
            return output, 0
        @property
        def stdout(self):
            self.remove = cmd.split("rmi")[-1].split(" ")

            class StdOut(object):
                @property
                def readline(self):
                    return ""  # just skip iterate stdout
            return StdOut()

    return MockProcess()



def test_docker_clean_old():
    with mock.patch("subprocess.Popen", side_effect=mock_process) as proc:
        docker_clean_old()
        proc.called


