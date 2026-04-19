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

### PC crash or OS reinstall without prior deactivation

!!! warning
    Reinstalling without deactivating first leaves an orphaned activation slot.
    The old slot cannot be freed automatically — the machine no longer exists to send a deactivation request.

If you hit the activation limit because of an orphaned slot, **contact support**:

**[support@neurocontrarian.com](mailto:support@neurocontrarian.com)**

Include the first 4 characters of your license key. We will manually free the orphaned slot from our dashboard.

!!! tip "Prevent this"
    Always open **Preferences → License → Deactivate** before reinstalling your OS or wiping a machine.

### Accidentally deactivated your license

No problem. Simply re-activate on the same device — this reuses the same slot. Your activation count does not increase.

| Step | Slots used |
|------|-----------|
| Before accidental deactivation | 3 / 3 |
| After deactivation | 2 / 3 |
| After re-activation on same device | 3 / 3 |

### Trying to activate on a 4th device

If your 3 slots are all in use, activation will fail with an error.

**Option 1** — Free a slot voluntarily: open RemoteX on one of your 3 active devices, go to **Preferences → License → Deactivate**, then activate on the new device.

**Option 2** — If a slot is orphaned (old device no longer accessible): contact support at [support@neurocontrarian.com](mailto:support@neurocontrarian.com).

!!! note
    The LemonSqueezy customer portal does **not** allow self-service instance deactivation. To free a slot you must either use the Deactivate button inside RemoteX, or contact support.

---

## Key sharing policy

Each license key is personal and non-transferable. At activation, RemoteX verifies that the email you enter matches the purchase email on record. Keys detected on more than 3 devices simultaneously will be revoked without refund.
