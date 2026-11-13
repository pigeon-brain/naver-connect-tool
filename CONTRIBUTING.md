# Contributing

Keep device access separate from the preview. Do not add subprocess, USB, ADB, network, or persistent-write calls to the preview.

Before a pull request:

1. Run `python -m unittest discover -p "test_*.py"` on Windows with Tkinter.
2. Run `python scripts/check_public_tree.py` from a clean public checkout.
3. Add Korean, English and Japanese strings for visible UI changes. Preserve user inputs when switching language.
4. Use mocks for write paths. Do not run CI against a connected terminal.
5. Describe the exact hardware/software combination for any claimed device validation. Distinguish success responses from actual readback or boot verification.

Never attach firmware dumps, payment data, certificates, pairing codes, device identifiers or unreviewed logs to an issue or pull request. Do not replace identity, backup, hash, slot or write-boundary checks with permissive fallbacks.
