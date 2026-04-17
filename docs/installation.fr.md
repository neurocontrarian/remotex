# Installation

## Prérequis

- Linux (X11 ou Wayland)
- Python 3.10 ou version ultérieure
- GTK 4 + libadwaita

## Depuis les sources

C'est la méthode recommandée jusqu'à ce que le paquet Flatpak soit disponible.

### 1. Installer les dépendances système

=== "Debian / Ubuntu / Linux Mint"

    ```bash
    sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 \
      libgtk-4-1 python3-gi-cairo libglib2.0-bin git
    ```

=== "Fedora"

    ```bash
    sudo dnf install python3-gobject gtk4 libadwaita \
      python3-cairo glib2 git
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S python-gobject gtk4 libadwaita \
      python-cairo glib2 git
    ```

### 2. Cloner et lancer

```bash
git clone https://github.com/neurocontrarian/remotex.git
cd remotex
./run_dev.sh
```

`run_dev.sh` gère tout automatiquement :

- Crée un environnement virtuel Python
- Installe les dépendances Python (`fabric`, `tomli_w`, `paramiko`)
- Compile le schéma GSettings
- Lance RemoteX

Le premier lancement initialise votre grille de boutons avec 34 boutons par défaut.

## Flatpak *(bientôt disponible)*

Un paquet Flatpak sera publié sur Flathub. En attendant, utilisez l'installation depuis les sources ci-dessus.

## Mise à jour

```bash
cd remotex
git pull
./run_dev.sh
```
