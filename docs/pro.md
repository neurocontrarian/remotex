# RemoteX Pro

## Free vs Pro

| | Free | Pro |
|--|------|-----|
| Local command execution | Unlimited | Unlimited |
| Default buttons (use) | Unlimited | Unlimited |
| Default buttons (edit) | Read-only | Editable |
| Custom buttons | **3** | Unlimited |
| SSH machines | — | Unlimited |
| Multi-machine buttons | — | ✓ |
| Multi-select + group actions | — | ✓ |
| Button themes (Cards, Neon, Retro…) | — | ✓ |
| Custom CSS theme | — | ✓ |
| Config backup / restore | — | ✓ |

!!! note
    Default buttons (Linux Essentials, Development) are always **visible, executable and deletable** on the free tier. Only editing their settings requires Pro.

## Pricing

- **$20 / year** — yearly license, renew to keep Pro access
- **$40 lifetime** — one-time purchase, no renewal

[Get a license →](https://neurocontrarian.lemonsqueezy.com/checkout/buy/f2b9451a-588d-49c2-b1ed-1afe21ffd9e2){ .md-button .md-button--primary }

## Activating your license

1. Open **Preferences** (`Ctrl+,`)
2. Scroll to the **License** section
3. Paste your license key in the field
4. Click **Activate Pro**

Your key is validated and stored locally at `~/.config/remotex/license.key`. An internet connection is required for the initial activation.

## Yearly license — renewal

A yearly license expires 365 days after activation. RemoteX shows a warning toast 30 days before expiry.

After expiry, free tier limits apply again — your buttons and machines are **not deleted**, but custom buttons beyond 3 become temporarily hidden.

Renew from **Preferences → License → Renew license**.

## Deactivating

To remove the license from a device: **Preferences → License → Deactivate license**.

## Backup and restore *(Pro)*

Export and import your full configuration from **Preferences**:

- **Buttons & Settings backup** — exports buttons and preferences to a `.rxbackup` file
- **Machines backup** — exports SSH machine definitions to a `.rxmachines` file (SSH private keys are never included)

Restore from the same Preferences section. Importing buttons merges with existing default buttons — newly added defaults are never lost.
