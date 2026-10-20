# Contributing

Changes to the `iac_blueprint.ceph` contract must update validation, README, examples, and validation tests together. Keep all cluster operations explicit and idempotent. Any OSD support requires explicit device identities, preflight checks, an unmistakable destructive opt-in, and disposable multi-host tests before implementation. Do not claim platform coverage without reproducible tests.

Activate the shared environment as described in `TESTING.md`. Run syntax, lint, and the focused Molecule scenario. Do not install dependencies in this repository or create a project virtualenv.
