# Activating your license

Welcome to Commandeck Pro! This guide walks you through activating your license for the first time.

!!! tip "What you'll need"
    - Your **license key** (sent in your purchase email from LemonSqueezy)
    - The **email address** you used when buying
    - An **internet connection** (required for the first activation only)

---

## Download and install

Your purchase email from LemonSqueezy contains a **Files** link. Click it to download `Commandeck-Pro-VERSION-x86_64.AppImage`.

Then make it executable and run it:

```bash
chmod +x Commandeck-Pro-*-x86_64.AppImage
./Commandeck-Pro-*-x86_64.AppImage
```

!!! info "System requirements"
    None — the Pro AppImage is self-contained (Python, Qt, and every dependency are
    bundled). If your distro reports a missing Qt platform plugin on launch, install
    `libxcb-cursor0`:
    ```bash
    # Ubuntu / Mint / Debian
    sudo apt install libxcb-cursor0

    # Fedora
    sudo dnf install xcb-util-cursor
    ```

The Pro AppImage is self-contained — all SSH libraries (Paramiko, cryptography, etc.) are bundled. No `pip install` needed.

---

## Step-by-step activation

1. **Open Commandeck** — make sure you're running the **Pro build**, not the Free build. ([What's the difference?](../pro.md#free-vs-pro))

2. **Open Preferences** with `Ctrl + ,` or via the hamburger menu → *Preferences*.

3. **Scroll to the *License* section.**

    ![License section in Preferences](../assets/license-section.png)

4. **Paste your license key** in the *License key* field.

5. **Enter the email** you used at purchase in the *Email* field.

    !!! warning "Email must match exactly"
        We compare what you type against the email LemonSqueezy has on file for the purchase. If it doesn't match, activation is refused — no slot is consumed.

6. Click **Activate Pro**.

7. Within a few seconds, the dialog refreshes and shows:
    - Your license **type** (Yearly)
    - The **expiry date**
    - Your **activation count** (e.g. *1 / 3*)

That's it — every Pro feature is now unlocked. SSH machines, multi-machine buttons, themes, backup, MCP server, all available.

---

## What happens next

| When | What happens |
|---|---|
| Right after activation | All Pro features unlock immediately |
| Every 24 hours | Commandeck silently re-validates your license online (no UI, no slowdown) |
| 30 days before expiry | A toast warns you that your subscription is about to renew |
| Day of expiry | LemonSqueezy renews your subscription automatically — nothing to do |
| If renewal fails | A 3-day grace period kicks in before Pro features lock |

If your subscription lapses, **your data is never deleted**. Buttons, machines, settings — all preserved. Re-activate any time and everything comes back.

---

## Troubleshooting

### *"This license key is registered to a different email."*

The email you typed doesn't match the one on the LemonSqueezy purchase. Double-check the receipt email you got from LemonSqueezy and use that exact address (case doesn't matter, but typos do).

### *"You have reached the maximum of 3 activations."*

You've used all 3 device slots for this license. Open Commandeck on one of your active devices, go to **Preferences → License → Deactivate**, then come back and activate here.

If you can't access any of your previously activated devices (lost laptop, OS reinstalled without deactivating, etc.), [contact support](mailto:neurocontrarian@gmail.com) — we'll free the orphaned slot from the dashboard.

See the full [License & Devices guide](license-devices.md) for every scenario.

### *"Network error — could not reach the license server."*

The first activation **requires** an internet connection (we check the key against LemonSqueezy). Make sure Commandeck can reach `api.lemonsqueezy.com` — corporate proxies and strict firewalls may block it.

After the first activation, Commandeck works offline. We only re-check once every 24 hours, and there's a 3-day grace period if the network is down.

### *I don't see a "License" section in Preferences*

You're running the **Free build**. The Free build has no license system — there's nothing to activate. To use Pro, [download the Pro build](../pro.md#download) and run it instead. Your buttons, machines and settings will be picked up automatically (same config directory).

---

## Where to go from here

- **[Add your first SSH machine](../ssh.md)** — the Pro feature most people start with
- **[Create a multi-machine button](../buttons.md#multi-machine-buttons)** — run one command on a fleet
- **[License & Devices](license-devices.md)** — everything about the 3-device limit, OS reinstalls, migrations
- **[Refund policy](../legal/refund.md)** — 14 days, no questions asked

Need anything else? [Email support](mailto:neurocontrarian@gmail.com) — we read every message.
