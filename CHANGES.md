
Changes
=======

Unreleased
---------------------

* Add ``docker-tools`` with cleanup operation of old and unused images.

0.3.1 (2020-04-23)
---------------------

* Fix parsing of output file extension when no explicit format was specified by ``--json`` or ``--yaml``.

0.3.0 (2020-04-21)
---------------------

* Add ``--indent`` argument to specify the output indentation.
* Fix incorrect object used for writing YAML format.

0.2.0 (2020-04-21)
---------------------

* Add ``--json`` and ``--yaml`` arguments to specify an output format not matching with the output file extension.
* Add ``--ignore`` argument to ignore validation of input file extension. Will try parsing either JSON/YAML.
* Add ``--version`` argument to keep track of any applied updates. 
* Bump ``JSON <=> YAML`` convert tool to ``0.2.0``.
* Fix current directory not used to call script from anywhere.

0.1.0 (2020-04-21)
---------------------

### Changes

* Add ``JSON <=> YAML`` conversion tool (version ``0.1.0`` but no ``--version`` argument yet to retrive it).
