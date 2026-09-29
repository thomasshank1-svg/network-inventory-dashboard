import sqlite3
import unittest

import domain


class NetworkDomainTest(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        domain.init(self.db)

    def test_invalid_ip_rejected(self):
        with self.assertRaises(ValueError):
            domain.handle("POST", "/api/devices", {"hostname": "bad", "ip": "999.1.1.1"}, self.db)

    def test_status_update(self):
        domain.handle("POST", "/api/status", {"id": 1, "status": "Offline", "notes": "Cable issue"}, self.db)
        self.assertEqual(self.db.execute("SELECT status FROM devices WHERE id=1").fetchone()[0], "Offline")


if __name__ == "__main__":
    unittest.main()
