# RemoteX Pro

RemoteX comes in two builds: **Free** (open source, local execution only) and **Pro** (proprietary, full feature set with SSH and AI integration).

## Free vs Pro

| | Free | Pro |
|--|------|-----|
| Local command execution | Unlimited | Unlimited |
| Custom buttons | Unlimited | Unlimited |
| Default buttons | Visible, executable, deletable | Editable |
| SSH machines | — | Unlimited |
| Multi-machine buttons | — | ✓ |
| Multi-select + group actions | — | ✓ |
| Button themes (Bold, Phone, Neon, Retro…) | — | ✓ |
| Custom CSS theme | — | ✓ |
| Execution profiles | — | ✓ |
| Config backup / restore | — | ✓ |
| MCP server (AI integration) | — | ✓ |
| AI button execution | — | ✓ |

!!! note
    Free and Pro are **separate downloads**, not the same binary with a license unlock. The Free build does not contain any Pro code.

## Pricing

**$29 / year** — yearly license, **automatically renewed** at $29 each year unless cancelled.

You can cancel anytime from the LemonSqueezy customer portal (the link is in your purchase email). Cancellation prevents the next renewal — your current period continues until its expiry date, and Pro features stay available until then.

A lifetime option may be offered later as a limited event. At launch, only the yearly license is available.

[Get a license →](https://neurocontrarian.lemonsqueezy.com/checkout/buy/9c16845a-8ab6-4a36-b8da-9874d9d64f33){ .md-button .md-button--primary }

## 14-day free trial

The Pro build includes an automatic **14-day trial** that starts the first time you launch it. No license key, no payment, no email capture — every Pro feature is available immediately.

A few days before the trial ends, RemoteX shows an in-app offer with a discount code. After day 14, Pro features become read-only (greyed out) — your buttons, machines and settings are **never deleted**.

To continue using Pro, activate a license from **Preferences → License**.

## Activating your license

1. Open **Preferences** (`Ctrl+,`)
2. Scroll to the **License** section
3. Enter the email address used for purchase
4. Paste your license key
5. Click **Activate Pro**

An internet connection is required for the initial activation. The license is then validated offline daily.

## Yearly renewal

A yearly license expires 365 days after activation. RemoteX shows a warning toast 30 days before expiry.

After expiry, free-tier limits apply again — your buttons and machines are **not deleted**, but Pro-only features (SSH, MCP, multi-select, themes, etc.) become unavailable until you renew.

Renew from **Preferences → License → Renew license**.

## Deactivating

To remove the license from a device: **Preferences → License → Deactivate license**.

This frees up an activation slot so you can use the same key on a different device. Your Pro license allows up to 3 simultaneous activations on devices you personally use — see [License & Devices](pro/license-devices.md) for details.

Free-tier limits apply immediately after deactivation. Your buttons are not deleted; Pro features are restored when you reactivate.

## Execution profiles *(Pro)*

Create reusable execution contexts that combine a target user, a working directory, and a sudo password into a single named profile.

Assign a profile to any button — when it runs, the command executes as the specified user in the specified directory, with the sudo password fed automatically (no terminal prompt).

Profiles work for both local and remote (SSH) execution, including **Open in terminal** mode.

Manage profiles from the hamburger menu → **Manage Profiles**.

---

## Backup and restore *(Pro)*

Export and import your full configuration from **Preferences**:

- **Buttons & Settings backup** — exports buttons and preferences to a `.rxbackup` file
- **Machines backup** — exports SSH machine definitions to a `.rxmachines` file (SSH private keys are never included)

Restore from the same Preferences section. Importing buttons merges with existing default buttons — newly added defaults are never lost.

---

## AI integration *(Pro)*

The MCP server lets AI assistants like Claude, Cursor or Open WebUI read, edit and execute your buttons through a single secure connection. See [AI Integration (MCP)](pro/mcp.md) for full setup and security details.
