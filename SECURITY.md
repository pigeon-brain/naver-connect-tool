# Security and device-data handling

Do not put private dumps, payment material, credentials, pairing codes, identifiers, or unredacted logs in public issues. Describe the affected operation and software version without the sensitive data. When the repository is published, use its private security reporting channel if enabled; no contact address is provided in this unpublished preparation.

The preview must remain unable to execute external processes or device commands. Device-writing paths must fail closed on an identity, backup, format, hash, mode, or readback mismatch. This project has no automatic stock-restoration guarantee. An image-write success response is not a completed boot test.

GitHub workflows test code and simulated state only. They must not download private firmware or interact with hardware.
