# License & Devices

!!! tip "Pro feature"
    A license key is required to activate [RemoteX Pro](../pro.md).

Each license key allows **3 simultaneous activations** on your own devices (personal use only).

The current count is displayed in **Preferences → License → Activations**.

---

## Activating on a new device

1. Open **Preferences** (`Ctrl+,`) on the device
2. Scroll to the **License** section
3. Enter your license key and the email address used at purchase
4. Click **Activate Pro**

An internet connection is required for the initial activation.

---

## Common scenarios

### You have up to 3 devices (desktop + laptop + server)

Activate on each device normally. Each activation consumes one slot.

| Device | Action | Slots used |
|--------|--------|-----------|
| Desktop | Activate | 1 / 3 |
| Laptop | Activate | 2 / 3 |
| Home server | Activate | 3 / 3 |

### Moving to a new computer (planned migration)

You want to replace an old machine with a new one.

1. On the **old machine**, open **Preferences → License → Deactivate** — this frees one slot (3 → 2)
2. Set up the new machine and install RemoteX
3. Activate your license on the new machine (2 → 3)

Net result: same slot count, no slot lost.

### OS reinstall — you remembered to deactivate first

Same as the planned migration above. Deactivate before reinstalling, then re-activate afterwards. The slot is freed and reused — your count stays the same.

### OS reinstall — you forgot to deactivate first

After reinstalling, your old activation slot still exists on LemonSqueezy (the old machine-id is still registered). Activating on the fresh install consumes a new slot.

If you hit the 3-device limit because of this orphaned slot:

1. Open RemoteX on any other device that is still activated and deactivate from **Preferences → License → Deactivate** to free a slot, then retry
2. If you have no other active device to deactivate from, [contact support](mailto:neurocontrarian@gmail.com) — we will free the orphaned slot manually from the dashboard

!!! warning "Deactivate before reinstalling"
    To avoid this situation, always open **Preferences → License → Deactivate** before reinstalling or formatting your OS.

### Accidentally deactivated your license

No problem. Simply re-activate on the same device — this reuses the same slot. Your activation count does not increase.

| Step | Slots used |
|------|-----------|
| Before accidental deactivation | 3 / 3 |
| After deactivation | 2 / 3 |
| After re-activation on same device | 3 / 3 |

### Trying to activate on a 4th device

If your 3 slots are all in use, activation will fail with an error.

Open RemoteX on one of your 3 active devices, go to **Preferences → License → Deactivate**, then activate on the new device.

!!! note
    The LemonSqueezy customer portal does **not** allow self-service instance deactivation. To free a slot, use the **Deactivate** button inside RemoteX on one of your active devices.

---

## Key sharing policy

Each license key is personal and non-transferable. At activation, RemoteX verifies that the email you enter matches the purchase email on record. Keys detected on more than 3 devices simultaneously will be revoked without refund.
