"""Pure address fixtures; no backend access or host mutation."""

import unittest

from address_preflight import validated_network


class AddressPreflightTests(unittest.TestCase):
    def test_allocated_network(self):
        self.assertEqual(
            validated_network(["10.60.1.10", "10.60.1.11", "10.60.1.12"], "10.60.1.0/24"),
            "10.60.1.0/24",
        )

    def test_rejects_mismatches_duplicates_and_non_host_addresses(self):
        for addresses, subnet in (
            (["10.60.1.10", "10.60.1.11", "10.60.2.12"], "10.60.1.0/24"),
            (["10.60.1.10", "10.60.1.11", "10.60.1.12"], "10.60.2.0/24"),
            (["10.60.1.10"] * 3, "10.60.1.0/24"),
            (["10.60.1.10", "10.60.1.11"], "10.60.1.0/24"),
            (["10.60.1.0", "10.60.1.11", "10.60.1.12"], "10.60.1.0/24"),
            (["10.60.1.255", "10.60.1.11", "10.60.1.12"], "10.60.1.0/24"),
            (["8.8.8.8", "8.8.8.9", "8.8.8.10"], "8.8.8.0/24"),
            (["fd00::1", "fd00::2", "fd00::3"], "fd00::/64"),
            (["10.60.1.10", "10.60.1.11", "10.60.1.12"], "10.60.0.0/16"),
            (["invalid", "10.60.1.11", "10.60.1.12"], "10.60.1.0/24"),
        ):
            with self.subTest(addresses=addresses, subnet=subnet):
                with self.assertRaises(ValueError):
                    validated_network(addresses, subnet)


if __name__ == "__main__":
    unittest.main()
