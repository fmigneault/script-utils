# script-utils

A bunch of scripts to be used as utility tools.

All tools employ either low-level ``bash`` or ``python`` scripts with a minimal amount of dependencies. 

## convert-tools

Convert items between corresponding formats.

- JSON <=> YAML
    - `json2yaml`
    - `yaml2json`
    - `yml2json`

## docker-tools

Run operations on docker images.

- Conditional Cleanup
    - `docker-clean-unused`
    - `docker-clean-old`

## merge-tools

Merging operations between files of similar or complementary content.

- CWL => OGC-API Process deploy payload: `merge_cwl_app_deploy`
