# Test Packages

These dummy packages can be used when testing USB monster. Their format follows
Balena Etcher .zip format which is used in distributing Abitti images.

 * `koe-etcher-pass.zip` contains ~100M random image file.
 * `koe-etcher-fail.zip` equals with the "pass" version except the sha256 hash has been
   tampered to cause checksum failure.
 * `koe-etcher-noversion.zip` equals with the "pass" version except the
   `ytl/.meta/manifest.json` file does not contain version string.
