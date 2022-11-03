# pylint: disable=too-few-public-methods,missing-module-docstring
# pylint: disable=missing-function-docstring,missing-class-docstring
import unittest

from pipcompilemulti.options import OPTIONS
from pipcompilemulti.features.add_hashes import AddHashes


class AddHashesTestCase(unittest.TestCase):
    def setUp(self):
        self._add_hashes = AddHashes(FakeController())
        OPTIONS[self._add_hashes.OPTION_NAME] = ['test']
        self._add_hashes.on_discover([
            {'in_path': 'base', 'refs': []},
            {'in_path': 'test', 'refs': ['base']},
            {'in_path': 'docs', 'refs': []},
        ])

    def test_pin_options(self):
        assert self._add_hashes.pin_options('base') == ['--generate-hashes']
        assert not self._add_hashes.pin_options('docs')


class FakeController():
    def compose_input_file_path(self, name):
        return name
