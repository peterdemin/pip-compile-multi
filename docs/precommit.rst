Verify as pre-commit hook
=========================

To verify that ``pip-compile-multi`` has been run after changing ``.in`` files as a `PreCommit`_ hook, just add the following to your local repo's ``.pre-commit-config.yaml`` file:

.. code-block:: yaml

    - repo: https://github.com/peterdemin/pip-compile-multi
      rev: v1.3.2
      hooks:
        - id: pip-compile-multi-verify

.. _PreCommit: https://pre-commit.com/
