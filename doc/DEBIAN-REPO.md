# Debian Repo Management

## Creating a Key

Generate a key:

`gpg --gen-key` or `gpg --full-generate-key`
 * RSA, 4096 bits
 * Key does not expire
 * Real name: "Abitti Team"
 * Email address: "abitti@ylioppilastutkinto.fi"
 * No passphrase

Export an ASCII version of the key. You will publish this later.

Get the key hash. You will need to change this to `conf/distributions` (the has below is `3505342F`):

```
$ gpg --list-key
/home/username/.gnupg/pubring.gpg
------------------------------
pub   4096R/3505342F 2019-05-25
uid                  Abitti Team <abitti@ylioppilastutkinto.fi>
```

Another example:

```
gpg --list-key
gpg: checking the trustdb
gpg: marginals needed: 3  completes needed: 1  trust model: pgp
gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
/home/username/.gnupg/pubring.kbx
------------------------------
pub   rsa4096 2019-05-28 [SC]
      0EEA516CC168C3078D93CEAEF0CB5A7157202474
uid           [ultimate] Abitti Team <abitti@ylioppilastutkinto.fi>
```

## Exporting keys from gpg keychain to files

  1. `gpg --output usb-monster-repo_pub.gpg --armor --export 0EEA516CC168C3078D93CEAEF0CB5A7157202474`
  1. `gpg --output usb-monster-repo_sec.gpg --armor --export-secret-key 0EEA516CC168C3078D93CEAEF0CB5A7157202474`

Now you have public and private keys.

## Importing keys from files to gpg keychain

 1. `gpg --import usb-monster-repo_pub.gpg`
 1. `gpg --allow-secret-key-import --import usb-monster-repo_sec.gpg`

## Publish the key

`gpg --armor --export abitti@ylioppilastutkinto.fi --output abitti@ylioppilastutkinto.fi.gpg.key  >docs/gpg.key`

## Import the key

To import the key to the client:

`sudo bash -c 'wget -O - https://URL-TO-DOCS/gpg.key | apt-key add -'`
