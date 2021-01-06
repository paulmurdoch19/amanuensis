"""
Notes on frequently disabled pylint warnings/errors:

* ``unsubscriptable-object``: because ``amanuensis.dictionary`` must be
  initialized later by the application using amanuensis, it appears to
  pylint that operations such as ``dictionary.schema[entity_type]`` should not
  work.
* ``unsupported-membership-test``: again because of
  ``amanuensis.dictionary``.
"""

from .blueprint import create_blueprint
