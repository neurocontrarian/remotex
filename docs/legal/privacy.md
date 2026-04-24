# Privacy Policy

*Last updated: April 2026*

## What data we collect

RemoteX collects minimal data, strictly necessary for license validation.

### At purchase (via LemonSqueezy)

Your email address and payment information are collected by [LemonSqueezy](https://www.lemonsqueezy.com), our payment processor. We receive only your email address for license validation purposes. We do not receive or store your payment card details.

### At license activation

When you activate a Pro license, the following data is transmitted to LemonSqueezy's API:

- Your license key
- An anonymous device identifier (`/etc/machine-id`, hashed — not linked to any personal identity)
- The name of the activation (your hostname, optional)

This data is used solely to verify that your license is valid and to manage your activation slots (max 3 devices).

### Stored locally on your machine

RemoteX stores the following files in `~/.config/remotex/`:

- `buttons.toml` — your button configuration
- `machines.toml` — your SSH machine definitions (no private keys)
- `profiles.toml` — your execution profiles (sudo passwords are encoded with a machine-specific key, not transmitted anywhere)

None of these files are transmitted to any server. The license key and activation metadata are stored locally and used only during validation calls to LemonSqueezy.

## What we do not collect

- We do not collect analytics or usage data
- We do not track which commands you run
- We do not have access to your SSH credentials or private keys
- We do not use cookies or web tracking

## Third-party services

License validation is handled by [LemonSqueezy](https://www.lemonsqueezy.com). Their privacy policy applies to data they process. Validation calls are made at activation and periodically (daily) when the app is running.

## Data retention

We do not store any personal data on our servers. All your configuration data remains on your local machine.

## Your rights

You may request deletion of your account and associated data by contacting us. Deactivating your license removes the device activation record from LemonSqueezy's servers.

## Changes to this Policy

We reserve the right to update this Privacy Policy at any time, at our sole discretion. Changes become effective immediately upon posting to this page. The "Last updated" date at the top reflects the most recent revision. We encourage you to review this page periodically.

## Contact

[neurocontrarian@gmail.com](mailto:neurocontrarian@gmail.com)
