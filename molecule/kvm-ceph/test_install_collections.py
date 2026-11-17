"""Fixture-only guard tests; never invoke Galaxy or create test guests."""

import json
import os
from pathlib import Path
import runpy
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import uuid


ROLE = Path(__file__).resolve().parents[2]
INSTALL = runpy.run_path(str(Path(__file__).with_name("install-collections")))


class ManagedGalaxyGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            dir="/tmp/opencode" if Path("/tmp/opencode").is_dir() else None,
        )
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.run_id = str(uuid.uuid4())
        root = self.home / ".idarsi-test-runs"
        run = root / self.run_id
        self.ephemeral = root / ".work" / self.run_id / "ephemeral"
        for directory in (root, run, root / ".work", self.ephemeral.parent, self.ephemeral):
            directory.mkdir(mode=0o700)
        manifest = run / "manifest.json"
        manifest.write_text(json.dumps({
            "id": self.run_id, "uid": os.getuid(), "backend": "kvm",
            "scenario": "kvm-ceph", "status": "running", "role": str(ROLE),
        }))
        manifest.chmod(0o600)
        self.env = {
            "IDARSI_RUN_ID": self.run_id,
            "MOLECULE_EPHEMERAL_DIRECTORY": str(self.ephemeral),
            "ANSIBLE_COLLECTIONS_PATH": "/shared/collections",
        }

    def validate(self):
        return INSTALL["validated_destination"](self.env, self.home, ROLE)

    def test_supervised_destination_and_mocked_galaxy(self):
        destination = self.validate()
        self.assertEqual(destination, self.ephemeral / "collections")
        self.assertTrue(destination.is_dir())
        with (patch.dict(os.environ, self.env),
              patch.object(INSTALL["pwd"], "getpwuid", return_value=SimpleNamespace(pw_dir=str(self.home))),
              patch.object(INSTALL["subprocess"], "run") as galaxy):
            self.assertEqual(INSTALL["main"](), 0)
        galaxy.assert_called_once()
        args, kwargs = galaxy.call_args
        self.assertEqual(args[0], [
            "ansible-galaxy", "collection", "install", "-r",
            "molecule/kvm-ceph/requirements.yml", "--collections-path",
            str(destination), "--force",
        ])
        self.assertIs(kwargs["check"], True)
        self.assertEqual(
            kwargs["env"]["ANSIBLE_COLLECTIONS_PATH"],
            str(destination) + ":/shared/collections",
        )

    def test_missing_empty_and_invalid_run_ids_fail_before_galaxy(self):
        for value in ("", "not-a-uuid", str(uuid.uuid4())):
            with self.subTest(value=value):
                self.env["IDARSI_RUN_ID"] = value
                with self.assertRaises((ValueError, FileNotFoundError)):
                    self.validate()

    def test_direct_invocation_never_starts_galaxy(self):
        with (patch.dict(os.environ, {"IDARSI_RUN_ID": "", "MOLECULE_EPHEMERAL_DIRECTORY": ""}),
              patch.object(INSTALL["subprocess"], "run") as galaxy):
            self.assertEqual(INSTALL["main"](), 1)
        galaxy.assert_not_called()

    def test_empty_relative_and_role_contained_directories_are_refused(self):
        for path in ("", "ephemeral", str(ROLE / "molecule/kvm-ceph")):
            with self.subTest(path=path):
                self.env["MOLECULE_EPHEMERAL_DIRECTORY"] = path
                with self.assertRaises(ValueError):
                    self.validate()

    def test_symlinked_collections_and_run_directory_are_refused(self):
        destination = self.ephemeral / "collections"
        destination.symlink_to(self.home)
        with self.assertRaises(ValueError):
            self.validate()
        destination.unlink()
        self.ephemeral.rmdir()
        self.ephemeral.symlink_to(self.home, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.validate()

    def test_nested_symlink_is_refused_before_galaxy(self):
        destination = self.ephemeral / "collections"
        destination.mkdir(mode=0o700)
        nested = destination / "ansible_collections"
        nested.mkdir(mode=0o700)
        (nested / "ansible").symlink_to(self.home, target_is_directory=True)
        with (patch.dict(os.environ, self.env),
              patch.object(INSTALL["pwd"], "getpwuid", return_value=SimpleNamespace(pw_dir=str(self.home))),
              patch.object(INSTALL["subprocess"], "run") as galaxy):
            self.assertEqual(INSTALL["main"](), 1)
        galaxy.assert_not_called()

    def test_inherited_empty_or_already_private_paths_get_private_first(self):
        destination = self.ephemeral / "collections"
        for inherited in ("", str(destination) + ":/shared/collections"):
            with self.subTest(inherited=inherited):
                self.env["ANSIBLE_COLLECTIONS_PATH"] = inherited
                with (patch.dict(os.environ, self.env),
                      patch.object(INSTALL["pwd"], "getpwuid", return_value=SimpleNamespace(pw_dir=str(self.home))),
                      patch.object(INSTALL["subprocess"], "run") as galaxy):
                    self.assertEqual(INSTALL["main"](), 0)
                expected = str(destination) + (":" + inherited if inherited else "")
                self.assertEqual(galaxy.call_args.kwargs["env"]["ANSIBLE_COLLECTIONS_PATH"], expected)

    def test_other_scenario_is_refused(self):
        manifest = self.home / ".idarsi-test-runs" / self.run_id / "manifest.json"
        content = json.loads(manifest.read_text())
        content["scenario"] = "other-role"
        manifest.write_text(json.dumps(content))
        with self.assertRaises(ValueError):
            self.validate()


if __name__ == "__main__":
    unittest.main()
