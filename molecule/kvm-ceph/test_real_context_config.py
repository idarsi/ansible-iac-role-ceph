"""Optional real-helper config smoke; no Galaxy or backend lifecycle actions."""

import fnmatch
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROLE = Path(__file__).resolve().parents[2]


@unittest.skipUnless(
    "IDARSI_TEST_ENVIRONMENT" in os.environ,
    "Real config smoke requires the shared tooling checkout",
)
class RealContextConfigTests(unittest.TestCase):
    def test_real_resolve_capabilities_and_collection_preservation(self):
        root = Path(os.environ["IDARSI_TEST_ENVIRONMENT"])
        self.assertTrue(root.is_absolute())
        helper = root / "scripts/scenario-context"
        bridge = root / "scripts/isolated_runs/molecule_config.py"
        self.assertTrue(helper.is_file())
        self.assertTrue(bridge.is_file())
        with tempfile.TemporaryDirectory(
            dir="/tmp/opencode" if Path("/tmp/opencode").is_dir() else None,
        ) as temporary:
            ephemeral = Path(temporary) / "ephemeral"
            ephemeral.mkdir(mode=0o700)
            env = dict(
                os.environ,
                MOLECULE_EPHEMERAL_DIRECTORY=str(ephemeral),
                PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"],
            )
            # Preserve inherited handoff markers: the real helper must validate
            # them, never silently turn an invalid supervised binding into direct.
            for action in ("resolve", "capabilities"):
                with self.subTest(action=action):
                    result = subprocess.run(
                        [sys.executable, str(helper), action, "--backend", "kvm",
                         "--scenario", "kvm-ceph", "--role", str(ROLE)],
                        cwd=ROLE, env=env, capture_output=True, text=True, timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    data = json.loads(result.stdout)
                    self.assertEqual(data["schema"], "idarsi.scenario-context/v1")
                    self.assertTrue(data["effective_config_validated"])
                    self.assertEqual(data["mode"], "direct")
                    self.assertIsNone(data["generation"])
                    self.assertEqual(data["ephemeral_directory"], str(ephemeral))
                    self.assertEqual(data["collections_directory"], str(ephemeral / "collections"))
            effective = subprocess.run(
                [sys.executable, str(bridge), str(ROLE / "molecule/kvm-ceph/molecule.yml")],
                cwd=ROLE, env=env, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(effective.returncode, 0, effective.stderr)
            config = json.loads(effective.stdout)
            self.assertIn(str(ephemeral / "collections/*"), config["driver"]["safe_files"])
            nested_manifest = ephemeral / "collections/ansible_collections/ansible/posix/MANIFEST.json"
            self.assertTrue(any(
                fnmatch.fnmatch(str(nested_manifest), pattern)
                for pattern in config["driver"]["safe_files"]
            ))
            self.assertFalse((ephemeral / "collections").exists())


if __name__ == "__main__":
    unittest.main()
