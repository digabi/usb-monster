# Debian Repo Management

## Creating a Key

Generate a key:

`gpg --gen-key`
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

## Publish the key

`gpg --armor --export abitti@ylioppilastutkinto.fi --output abitti@ylioppilastutkinto.fi.gpg.key  >docs/gpg.key`

## Import the key

To import the key to the client:

`sudo bash -c 'wget -O - https://URL-TO-DOCS/gpg.key | apt-key add -'`
