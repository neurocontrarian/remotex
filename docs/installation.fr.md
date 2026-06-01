# Installation

Commandeck fonctionne sur **Linux, macOS et Windows**. Chaque version liste les fichiers
des trois plateformes au même endroit :
**[GitHub Releases](https://github.com/neurocontrarian/commandeck/releases/latest)** — ce
lien pointe toujours vers la dernière version, ajoutez-le à vos favoris.

Toutes les versions **Pro** incluent un **essai gratuit de 14 jours** — sans compte,
sans carte. L'essai démarre automatiquement au premier lancement.

---

## Linux (AppImage)

Un seul fichier, aucune installation. Téléchargez-le, rendez-le exécutable, lancez-le.
L'AppImage est **autonome** : elle embarque Python, Qt et toutes les dépendances, il n'y
a donc rien à installer sur le système.

| Fichier | Quand l'utiliser |
|---------|------------------|
| `Commandeck-VERSION-Linux-x86_64.AppImage` | **Gratuit — Intel/AMD.** |
| `Commandeck-VERSION-Linux-ARM64.AppImage` | **Gratuit — ARM64** (Raspberry Pi 4+, serveur ARM, VM Apple Silicon). |
| `Commandeck-Pro-VERSION-Linux-x86_64.AppImage` | **Pro — Intel/AMD.** Essai de 14 jours inclus. |
| `Commandeck-Pro-VERSION-Linux-ARM64.AppImage` | **Pro — ARM64.** Essai de 14 jours inclus. |

Vous ne savez pas quel processeur vous avez ? Lancez `uname -m` — `x86_64` pour
Intel/AMD, `aarch64` pour ARM.

```bash
chmod +x Commandeck-*.AppImage
./Commandeck-*.AppImage
```

Si votre distribution signale un greffon de plateforme Qt manquant au lancement,
installez `libxcb-cursor0` :

=== "Debian / Ubuntu / Linux Mint"

    ```bash
    sudo apt install libxcb-cursor0
    ```

=== "Fedora"

    ```bash
    sudo dnf install xcb-util-cursor
    ```

=== "Arch Linux"

    ```bash
    sudo pacman -S xcb-util-cursor
    ```

---

## macOS (Apple Silicon)

| Fichier | Quand l'utiliser |
|---------|------------------|
| `Commandeck-VERSION-macOS-AppleSilicon.dmg` | **Gratuit.** |
| `Commandeck-Pro-VERSION-macOS-AppleSilicon.dmg` | **Pro.** Essai de 14 jours inclus. |

Ouvrez le `.dmg` et glissez **Commandeck** dans Applications.

L'application n'est **pas encore signée**, donc Gatekeeper la bloquera au premier
lancement. Faites un clic droit sur l'app → **Ouvrir** (puis confirmez), ou lancez :

```bash
xattr -dr com.apple.quarantine /Applications/Commandeck.app
```

---

## Windows (x86_64)

| Fichier | Quand l'utiliser |
|---------|------------------|
| `Commandeck-VERSION-Windows-x64.exe` | **Gratuit** — installeur (raccourci menu Démarrer + désinstallateur). |
| `Commandeck-Pro-VERSION-Windows-x64.exe` | Installeur **Pro**. Essai de 14 jours inclus. |

Lancez l'installeur. Il n'est **pas encore signé**, donc SmartScreen peut vous avertir :
cliquez sur **Informations complémentaires → Exécuter quand même**.

---

## Depuis les sources

Pour qui préfère installer depuis les sources ou contribuer. Fonctionne sur les trois
plateformes.

### Prérequis

- Python 3.10 ou plus récent
- Sous Linux : installez `libxcb-cursor0` si Qt signale un greffon de plateforme manquant
  (`sudo apt install libxcb-cursor0` sur Debian/Ubuntu/Mint)

### Cloner et lancer

```bash
git clone https://github.com/neurocontrarian/commandeck.git
cd commandeck
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python3 -m commandeck_qt
```

Le premier lancement remplit votre grille avec des boutons par défaut prêts à l'emploi.

## Mise à jour

```bash
cd commandeck
git pull
pip install -e ".[dev]"
python3 -m commandeck_qt
```
