"""Fixture-only context guards; never invoke Galaxy or create test guests."""

import json
import os
from pathlib import Path
import runpy
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import uuid

import scenario_context


ROLE = Path(__file__).resolve().parents[2]
INSTALL = runpy.run_path(str(Path(__file__).with_name("install-collections")))


class ContextGalaxyGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            dir="/tmp/opencode" if Path("/tmp/opencode").is_dir() else None,
        )
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.ephemeral = self.root / "actual-molecule-ephemeral"
        self.ephemeral.mkdir(mode=0o700)
        self.destination = self.ephemeral / "collections"
        self.env = {
            "IDARSI_TEST_ENVIRONMENT": str(self.root / "shared-tooling"),
            "MOLECULE_EPHEMERAL_DIRECTORY": str(self.ephemeral),
            "ANSIBLE_COLLECTIONS_PATH": "/shared/collections",
        }
        self.result = {
            "schema": "idarsi.scenario-context/v1",
            "mode": "direct", "effective_config_validated": True,
            "lifecycle_modes": ["direct", "supervised"],
            "role": str(ROLE), "scenario": "kvm-ceph", "backend": "kvm",
            "ephemeral_directory": str(self.ephemeral),
            "collections_directory": str(self.destination), "generation": None,
        }

    def resolve(self):
        completed = SimpleNamespace(stdout=json.dumps(self.result))
        with patch.object(scenario_context.subprocess, "run", return_value=completed) as helper:
            result = scenario_context.context("resolve", self.env)
        helper.assert_called_once()
        self.assertEqual(helper.call_args.args[0][1:], [
            str(self.root / "shared-tooling/scripts/scenario-context"), "resolve",
            "--backend", "kvm", "--scenario", "kvm-ceph", "--role", str(ROLE),
        ])
        self.assertEqual(helper.call_args.kwargs["env"], self.env)
        return result

    def install(self):
        # Validate helper output separately; this boundary never invokes a backend.
        result = self.resolve()
        with (patch.dict(os.environ, self.env, clear=True),
              patch.dict(INSTALL["main"].__globals__, context=lambda *args: result),
              patch.object(INSTALL["subprocess"], "run") as galaxy):
            status = INSTALL["main"]()
        return status, galaxy

    def test_direct_and_supervised_use_actual_ephemeral_without_allocating(self):
        for mode in ("direct", "supervised"):
            with self.subTest(mode=mode):
                self.result.update(mode=mode, generation=str(uuid.uuid4()) if mode == "supervised" else None)
                status, galaxy = self.install()
                self.assertEqual(status, 0)
                galaxy.assert_called_once()
                self.assertEqual(galaxy.call_args.args[0], [
                    "ansible-galaxy", "collection", "install", "-r",
                    "molecule/kvm-ceph/requirements.yml", "--collections-path",
                    str(self.destination), "--force",
                ])
                self.assertIs(galaxy.call_args.kwargs["check"], True)
                self.assertEqual(
                    galaxy.call_args.kwargs["env"]["ANSIBLE_COLLECTIONS_PATH"],
                    str(self.destination) + ":/shared/collections",
                )
                self.assertTrue(self.destination.is_dir())

    def test_invalid_context_identity_fails_closed(self):
        for key, value in (
            ("schema", "unknown"), ("mode", "unknown"), ("effective_config_validated", False),
            ("role", str(self.root)), ("scenario", "other"), ("backend", "podman"),
            ("collections_directory", str(self.root / "outside")),
        ):
            with self.subTest(key=key), patch.dict(self.result, {key: value}):
                with self.assertRaises(ValueError):
                    self.resolve()

    def test_missing_tooling_and_mismatched_actual_ephemeral_are_refused(self):
        for key, value in (
            ("IDARSI_TEST_ENVIRONMENT", ""), ("IDARSI_TEST_ENVIRONMENT", "relative"),
            ("MOLECULE_EPHEMERAL_DIRECTORY", str(self.root)),
        ):
            with self.subTest(key=key), patch.dict(self.env, {key: value}):
                with self.assertRaises(ValueError):
                    self.resolve()

    def test_partial_handoff_is_always_forwarded_for_strict_shared_validation(self):
        for marker in ("IDARSI_RUN_ID", "IDARSI_HANDOFF", "IDARSI_HANDOFF_UNKNOWN"):
            with self.subTest(marker=marker), patch.dict(self.env, {marker: ""}):
                error = scenario_context.subprocess.CalledProcessError(
                    1, ["scenario-context"], stderr="Partial or unsupported supervised handoff",
                )
                with patch.object(scenario_context.subprocess, "run", side_effect=error) as helper:
                    with self.assertRaisesRegex(ValueError, "Partial or unsupported"):
                        scenario_context.context("resolve", self.env)
                self.assertIn(marker, helper.call_args.kwargs["env"])

    def test_failed_context_does_not_start_galaxy(self):
        with (patch.dict(os.environ, self.env, clear=True),
              patch.dict(INSTALL["main"].__globals__, context=unittest.mock.Mock(side_effect=ValueError("invalid"))),
              patch.object(INSTALL["subprocess"], "run") as galaxy):
            self.assertEqual(INSTALL["main"](), 1)
        galaxy.assert_not_called()

    def test_symlinked_ephemeral_and_collections_are_refused(self):
        self.ephemeral.rmdir()
        self.ephemeral.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.resolve()
        self.ephemeral.unlink()
        self.ephemeral.mkdir(mode=0o700)
        self.destination.symlink_to(self.root, target_is_directory=True)
        status, galaxy = self.install()
        self.assertEqual(status, 1)
        galaxy.assert_not_called()

    def test_nested_links_writable_files_and_hardlinks_are_refused(self):
        self.destination.mkdir(mode=0o700)
        unsafe = self.destination / "unsafe"
        unsafe.symlink_to(self.root)
        for kind in ("symlink", "writable", "hardlink"):
            with self.subTest(kind=kind):
                if kind == "writable":
                    unsafe.unlink()
                    unsafe.write_text("{}")
                    unsafe.chmod(0o666)
                if kind == "hardlink":
                    unsafe.chmod(0o600)
                    (self.destination / "alias").hardlink_to(unsafe)
                status, galaxy = self.install()
                self.assertEqual(status, 1)
                galaxy.assert_not_called()

    def test_collection_lock_rejects_links_and_overlapping_writers(self):
        lock = self.ephemeral / ".ceph-collections.lock"
        lock.symlink_to(self.root / "outside")
        with self.assertRaises(OSError):
            with INSTALL["collection_lock"](self.ephemeral):
                self.fail("A symlink lock must never authorize installation")
        lock.unlink()
        with INSTALL["collection_lock"](self.ephemeral):
            with self.assertRaises(BlockingIOError):
                with INSTALL["collection_lock"](self.ephemeral):
                    self.fail("Concurrent Galaxy writes must fail closed")
        with INSTALL["collection_lock"](self.ephemeral):
            pass

    def test_inherited_empty_or_already_private_paths_get_private_first(self):
        for inherited in ("", str(self.destination) + ":/shared/collections"):
            with self.subTest(inherited=inherited):
                self.env["ANSIBLE_COLLECTIONS_PATH"] = inherited
                status, galaxy = self.install()
                self.assertEqual(status, 0)
                expected = str(self.destination) + (":" + inherited if inherited else "")
                self.assertEqual(galaxy.call_args.kwargs["env"]["ANSIBLE_COLLECTIONS_PATH"], expected)

    def test_private_exact_pin_precedes_inherited_collections(self):
        posix = self.destination / "ansible_collections/ansible/posix"
        posix.mkdir(parents=True, mode=0o700)
        manifest = posix / "MANIFEST.json"
        manifest.write_text(json.dumps({"collection_info": {"version": "2.1.0"}}))
        env = dict(self.env, ANSIBLE_COLLECTIONS_PATH=str(self.destination) + ":/shared")
        scenario_context.check_pin(self.ephemeral, env)
        manifest.write_text(json.dumps({"collection_info": {"version": "2.0.0"}}))
        with self.assertRaisesRegex(ValueError, "2.1.0"):
            scenario_context.check_pin(self.ephemeral, env)
        with self.assertRaisesRegex(ValueError, "precede"):
            scenario_context.check_pin(self.ephemeral, self.env)

    def test_inspect_current_generation_for_both_modes(self):
        for mode in ("direct", "supervised"):
            generation = str(uuid.uuid4())
            self.result.update(mode=mode, generation=generation, manifest={
                "id": generation, "role": str(ROLE), "scenario": "kvm-ceph",
                "backend": "kvm", "status": "running", "network": "owned",
                "subnet": "10.60.1.0/24",
            })
            with (self.subTest(mode=mode),
                  patch.object(scenario_context, "context", return_value=self.result),
                  patch.object(scenario_context, "check_pin"),
                  patch("builtins.print") as output):
                self.assertEqual(scenario_context.main(["10.60.1.10", "10.60.1.11", "10.60.1.12"]), 0)
                output.assert_called_once_with("10.60.1.0/24")
            self.result["manifest"]["id"] = str(uuid.uuid4())
            with (patch.object(scenario_context, "context", return_value=self.result),
                  patch.object(scenario_context, "check_pin")):
                self.assertEqual(scenario_context.main(["10.60.1.10", "10.60.1.11", "10.60.1.12"]), 1)

    def test_incomplete_mutation_never_reaches_guest_convergence(self):
        generation = str(uuid.uuid4())
        self.result.update(generation=generation, manifest={
            "id": generation, "role": str(ROLE), "scenario": "kvm-ceph",
            "backend": "kvm", "status": "running", "network": "owned",
            "subnet": "10.60.1.0/24", "operations": [{"id": "incomplete"}],
        })
        with (patch.object(scenario_context, "context", return_value=self.result),
              patch.object(scenario_context, "check_pin") as pin,
              patch("builtins.print") as output):
            self.assertEqual(scenario_context.main(["10.60.1.10", "10.60.1.11", "10.60.1.12"]), 1)
        pin.assert_not_called()
        self.assertIn("inspection only", output.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
