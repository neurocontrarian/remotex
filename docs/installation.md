# Installation

## Requirements

- Linux (X11 or Wayland)
- Python 3.10 or later
- GTK 4 + libadwaita

## From source

This is the recommended method until the Flatpak package is available.

### 1. Install system dependencies

=== "Debian / Ubuntu / Linux Mint"

    ```bash
    sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 \
      libgtk-4-1 python3-gi-cairo libglib2.0-bin wmctrl git
    ```

=== "Fedora"

    ```bash
    sudo dnf install python3-gobject gtk4 libadwaita \
      python3-cairo glib2 wmctrl git
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S python-gobject gtk4 libadwaita \
      python-cairo glib2 wmctrl git
    ```

### 2. Clone and run

```bash
git clone https://github.com/neurocontrarian/remotex.git
cd remotex
./run_dev.sh
```

`run_dev.sh` handles everything automatically:

- Creates a Python virtual environment
- Installs Python dependencies (`fabric`, `tomli_w`, `paramiko`)
- Compiles the GSettings schema
- Launches RemoteX

The first launch seeds your button grid with 34 default buttons.

## Flatpak *(coming soon)*

A Flatpak package will be published on Flathub. Until then, use the source install above.

## Updating

```bash
cd remotex
git pull
./run_dev.sh
```
