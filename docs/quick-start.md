# Quick Start

Get RemoteX running and your first button working in about two minutes.

## 1. Launch RemoteX

After [installing RemoteX](installation.md), run it from the project folder:

```bash
./run_dev.sh
```

The first launch seeds your grid with **34 default buttons** organised in two categories: Linux Essentials and Development. No setup needed — click any of them to run the command immediately.

![RemoteX main window with default buttons](assets/quick-start-grid.png)

## 2. Run a default button

Click **Disk Usage** to see your filesystem at a glance. A toast notification confirms success. Click it again while holding no modifier to just run it silently.

For commands that produce output (like Disk Usage), the result appears in a small dialog automatically.

## 3. Create your first custom button

1. Press **Ctrl+N** (or click **+** in the header bar)
2. Fill in **Label** — the text shown on the button
3. Fill in **Command** — any shell command, for example `ping -c 4 8.8.8.8`
4. Click **Save**

Your button appears in the grid. Click it to run the command.

!!! tip
    The free tier allows **3 custom buttons**. [RemoteX Pro](pro.md) removes this limit.

## 4. Organise with categories

In the button editor, type a name in the **Category** field (e.g. `Networking`). A pill tab appears in the category bar below the header. Click the pill to filter the grid to that category.

## 5. Next steps

| What you want to do | Where to look |
|---------------------|---------------|
| Understand every button field | [Button Editor](reference/button-editor.md) |
| Explore every UI element | [Main Window](reference/main-window.md) |
| Connect a remote server | [SSH Machines](reference/ssh-machines.md) |
| Adjust columns, size, theme | [Preferences](reference/preferences.md) |
| See real-world examples | [Use Cases](use-cases/home-server.md) |
