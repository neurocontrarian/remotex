# SSH & Multi-machine

!!! tip "Pro feature"
    SSH machines and multi-machine buttons require [RemoteX Pro](../pro.md).

This page covers the Pro-specific workflow for SSH: adding machines, assigning them to buttons, and using the machine picker. For a complete field-by-field reference of the Add Machine dialog, see [SSH Machines](../reference/ssh-machines.md).

---

## Adding your first machine

1. Open **Menu → Manage Machines**
2. Click **+** to open the Add Machine dialog
3. Fill in the machine name, host, SSH user, and key path
4. Click **Test** to verify the connection
5. Click **Save**

The machine is now available in every Button Editor.

For SSH key setup instructions (generating a key pair and copying it to the server), see [SSH key setup](../reference/ssh-machines.md#ssh-key-setup).

---

## Assigning a machine to a button

Open the Button Editor (create a new button or right-click an existing one → **Edit**).

In the **Target machines** section:

- Disable **Local** if you only want the remote machine
- Enable the machine(s) you want

Click **Save**. The button's tooltip now shows the target machine name.

---

## Single-machine buttons

When exactly one target is enabled, the command runs on that target immediately — no picker, no extra click. This is the most common setup.

---

## Multi-machine buttons

Enable two or more targets and the button becomes a multi-machine button. Each click opens the [machine picker](../reference/ssh-machines.md#the-machine-picker).

The picker lists every enabled target by name and icon. Select one and click **Run**.

### Mixing Local and remote

Enable **Local** alongside one or more SSH machines to include your own computer as an option in the picker. Useful for scripts that work identically on both environments.

### "All machines" shortcut

In the Button Editor, the **All machines** toggle at the top of the machine list selects every configured machine at once. This is convenient when you want a command like `df -h` available across your entire fleet without ticking boxes individually.

---

## Practical patterns

### Same command, multiple servers

Create one button with all target machines enabled. The picker lets you choose which server to query each time.

### Parallel commands across servers

Multi-machine buttons run on one machine per click (via the picker). For true parallel execution across multiple servers, open the button quickly for each machine in succession, or use a shell script that handles the SSH calls directly.

### Local + remote toggle

A button with both Local and a server machine enabled is useful for testing: run the command locally first to verify it works, then pick the server to deploy.

---

## Output modes

All three execution modes work over SSH. For interactive SSH sessions, use **Open in terminal** — RemoteX generates the correct `ssh -t` invocation automatically.

See [Output modes over SSH](../reference/ssh-machines.md#output-modes-over-ssh) for the full comparison.
