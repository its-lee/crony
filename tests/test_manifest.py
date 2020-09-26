import unittest
from crony import manifest

class ManifestTest(unittest.TestCase):

    def test_success(self):
        self.assertEqual('1.0.1', manifest.version)

    #def test_fail(self):
    #    self.assertEqual(15, -15)
