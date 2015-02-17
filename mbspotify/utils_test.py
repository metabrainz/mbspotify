import unittest
from mbspotify import utils


class UtilsTestCase(unittest.TestCase):

    def test_validate_uuid(self):
        self.assertTrue(utils.validate_uuid("123e4567-e89b-12d3-a456-426655440000"))
        self.assertFalse(utils.validate_uuid("not-a-uuid"))
