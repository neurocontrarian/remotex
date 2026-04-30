# Cas d'utilisation : Gestion d'un serveur domestique

Ce guide explique comment configurer RemoteX pour gérer un serveur domestique typique — une machine exécutant Plex, Pi-hole ou servant de NAS. L'objectif : réduire les tâches de maintenance courantes à un simple clic.

## Le scénario

Vous disposez d'un Raspberry Pi ou d'un mini-PC sur votre réseau domestique. Il exécute :

- **Plex Media Server** — votre serveur de streaming personnel
- **Pi-hole** — blocage des publicités à l'échelle du réseau
- **Samba** — partage de fichiers dans la maison

Vous en avez assez de vous connecter en SSH chaque fois que vous devez redémarrer un service ou vérifier l'utilisation du disque.

---

## Étape 1 — Ajouter le serveur comme machine SSH

Ouvrez **Menu → Gérer les machines → +** et renseignez :

| Champ | Exemple |
|-------|---------|
| Nom | `Serveur Maison` |
| Hôte | `192.168.1.50` |
| Utilisateur SSH | `pi` |
| Port | `22` |
| Chemin de la clé SSH | `~/.ssh/id_ed25519` |
| Icône | Serveur |

Si vous n'avez pas encore de clé SSH configurée, cliquez sur **Générer une clé SSH** puis **Copier la clé sur le serveur** et saisissez votre mot de passe une seule fois. Ensuite, cliquez sur **Tester** pour confirmer que la connexion fonctionne.

!!! tip "Fonctionnalité Pro"
    L'ajout de machines SSH nécessite [RemoteX Pro](../pro.md).

---

## Étape 2 — Créer une catégorie "Serveur Maison"

Dans l'éditeur de bouton, chaque bouton que vous créez pour ce serveur utilisera **Catégorie : Serveur Maison**. Cela les regroupe sous un onglet pastille dédié.

---

## Étape 3 — Créer les boutons

### Vérifier l'espace disque

| Champ | Valeur |
|-------|--------|
| Étiquette | `Utilisation disque` |
| Commande | `df -h` |
| Catégorie | `Serveur Maison` |
| Cible | `Serveur Maison` (votre machine SSH) |
| Mode d'exécution | `Afficher la sortie` |
| Icône | `drive-harddisk-symbolic` |

Affiche un récapitulatif de chaque système de fichiers sur le serveur. La boîte de dialogue de sortie s'ouvre automatiquement.

---

### Redémarrer Plex

| Champ | Valeur |
|-------|--------|
| Étiquette | `Redémarrer Plex` |
| Commande | `sudo systemctl restart plexmediaserver` |
| Catégorie | `Serveur Maison` |
| Cible | `Serveur Maison` |
| Mode d'exécution | `Silencieux` |
| Confirmer avant d'exécuter | Activé |
| Infobulle | `Redémarrer le service Plex Media Server` |
| Icône | `media-playback-start-symbolic` |

La boîte de dialogue de confirmation évite les redémarrages accidentels pendant qu'une personne regarde.

---

### Mettre à jour les paquets

| Champ | Valeur |
|-------|--------|
| Étiquette | `Mise à jour système` |
| Commande | `sudo apt update && sudo apt upgrade -y` |
| Catégorie | `Serveur Maison` |
| Cible | `Serveur Maison` |
| Mode d'exécution | `Afficher la sortie` |
| Infobulle | `Mettre à jour tous les paquets installés` |

Le mode **Afficher la sortie** vous permet de voir ce qui a été mis à jour.

---

### Vider le cache DNS de Pi-hole

| Champ | Valeur |
|-------|--------|
| Étiquette | `Vider DNS` |
| Commande | `pihole restartdns` |
| Catégorie | `Serveur Maison` |
| Cible | `Serveur Maison` |
| Mode d'exécution | `Silencieux` |

---

### Vérifier l'état de Samba

| Champ | Valeur |
|-------|--------|
| Étiquette | `État Samba` |
| Commande | `sudo systemctl status smbd nmbd` |
| Catégorie | `Serveur Maison` |
| Cible | `Serveur Maison` |
| Mode d'exécution | `Afficher la sortie` |

---

### Redémarrer le serveur

| Champ | Valeur |
|-------|--------|
| Étiquette | `Redémarrer le serveur` |
| Commande | `sudo systemctl reboot` |
| Catégorie | `Serveur Maison` |
| Cible | `Serveur Maison` |
| Mode d'exécution | `Silencieux` |
| Confirmer avant d'exécuter | Activé |
| Couleur | `#e01b24` (rouge — signal de danger) |
| Infobulle | `Redémarrer le serveur domestique — déconnecte tous les clients` |

---

## Étape 4 — Multi-machines : exécuter sur plusieurs serveurs

Si vous ajoutez ultérieurement un deuxième serveur (NAS, Pi de rechange), vous pouvez configurer des boutons ciblant plusieurs machines. Par exemple, un bouton **Mise à jour système** que vous souhaitez exécuter sur les deux :

1. Ouvrez l'éditeur de bouton pour le bouton **Mise à jour système** existant
2. Dans **Machines cibles**, activez à la fois `Serveur Maison` et votre deuxième machine
3. Enregistrez

Désormais, cliquer sur le bouton ouvre le [sélecteur de machine](../reference/ssh-machines.md#le-sélecteur-de-machine) — choisissez quel serveur mettre à jour, ou exécutez-le deux fois pour les deux.

---

## Résultat

Votre onglet de catégorie **Serveur Maison** vous donne accès en un clic à tout ce dont vous avez besoin. Sans terminal.

!!! tip
    Si vous gérez fréquemment le serveur tout au long de la journée, activez **Toujours au premier plan** dans le menu hamburger. RemoteX reste visible pendant que vous travaillez dans d'autres applications.
