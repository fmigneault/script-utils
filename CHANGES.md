
Changes
=======

1.2.0
---------------------

### convert-tools
* Add ``json2yml`` redirect to main ``JSON <=> YAML`` converter to have equivalent of ``yml2json`` (without ``a``). 

### docker-tools
* Change resolver to employ same path as the dry-run parser, but apply remove afterwards to ensure same results.
* Change flag ``-n`` to ``-k`` and rename long form ``--keep-count`` to ``--keep``.
* Add enforced removal (``f`` annotation) of untagged dangling image tags (``<none>`` name and/or version).
* Add ``--ignore-repo`` option to allow combination of similarly tagged images with/without repository prefix.
* Add basic tests to validate minimal features behaviour.

### merge-tools
* N/A

1.1.0 (2020-09-23)
---------------------

### convert-tools
* N/A

### merge-tools
* Add ``merge-tools`` with `CWL` insertion within an OGC-API Process as Application Package
  (see: [crim-ca/weaver](https://pavics-weaver.readthedocs.io/en/latest/) and 
  [crim-ca/application-packages](https://github.com/crim-ca/application-packages)).

1.0.0 (2020-06-17)
---------------------

### convert-tools
* N/A

### docker-tools
* Add ``docker-tools`` with cleanup operation of old and unused images.

0.3.1 (2020-04-23)
---------------------

### convert-tools
* Fix parsing of output file extension when no explicit format was specified by ``--json`` or ``--yaml``.

0.3.0 (2020-04-21)
---------------------

### convert-tools
* Add ``--indent`` argument to specify the output indentation.
* Fix incorrect object used for writing YAML format.

0.2.0 (2020-04-21)
---------------------

### convert-tools
* Add ``--json`` and ``--yaml`` arguments to specify an output format not matching with the output file extension.
* Add ``--ignore`` argument to ignore validation of input file extension. Will try parsing either JSON/YAML.
* Add ``--version`` argument to keep track of any applied updates. 
* Bump ``JSON <=> YAML`` convert tool to ``0.2.0``.
* Fix current directory not used to call script from anywhere.

0.1.0 (2020-04-21)
---------------------

### convert-tools
* Add ``JSON <=> YAML`` conversion tool (version ``0.1.0`` but no ``--version`` argument yet to retrive it).
