import unittest

from crony import manifest

class ManifestTest(unittest.TestCase):
    def test_pkgname_exists(self):
        manifest.pkgname
       
    def test_version_exists(self):
        manifest.version
        
    def test_description_exists(self):
        manifest.description
