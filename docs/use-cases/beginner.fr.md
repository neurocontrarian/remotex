# Cas d'utilisation : Guide pour débutants Linux

Vous venez d'installer RemoteX et vous ne savez pas par où commencer. Ce guide est fait pour vous. Vous n'avez pas besoin de connaître des commandes Linux — RemoteX inclut déjà 34 boutons prêts à l'emploi.

---

## Vous avez déjà 34 boutons

Au premier lancement de RemoteX, votre grille est remplie avec deux catégories de boutons préconfigurés :

- **Linux Essentials** (20 boutons) — informations système, réseau, disque, utilisateurs, logs et maintenance de base
- **Développement** (14 boutons) — git, docker, Python, Node et services système

Ces boutons sont prêts à l'emploi immédiatement. Aucune configuration nécessaire.

---

## Ce que fait chaque bouton par défaut

### Linux Essentials

| Bouton | Ce qu'il vous montre |
|--------|----------------------|
| **Utilisation disque** | Le remplissage de chaque partition (`df -h`) |
| **Utilisation mémoire** | Utilisation de la RAM et du swap (`free -h`) |
| **Charge CPU** | Moyennes de charge actuelles (`uptime`) |
| **Température** | Température du CPU si `lm-sensors` est installé |
| **Processus en cours** | Tous les processus, triés par utilisation CPU |
| **Interfaces réseau** | Vos adresses IP et cartes réseau |
| **Connexions actives** | Connexions TCP établies |
| **Ports ouverts** | Services en écoute sur votre machine |
| **Périphériques bloc** | Disques durs, clés USB, partitions (`lsblk`) |
| **Répertoires les plus grands** | Dossiers les plus volumineux sous `/` |
| **Informations système** | Version du noyau et distribution Linux |
| **Utilisateurs connectés** | Qui est actuellement connecté |
| **Dernières connexions** | Historique des connexions |
| **Services en échec** | Services qui ont planté ou n'ont pas démarré |
| **Journal système** | Les 50 dernières lignes du journal système |
| **Messages noyau** | Messages matériels et pilotes (`dmesg`) |
| **Vider la corbeille** | Vide votre dossier Corbeille |
| **Mise à jour système** | Met à jour votre système (fonctionne sur Ubuntu, Fedora, Arch) |
| **Redémarrer** | Redémarre l'ordinateur |
| **Éteindre** | Éteint l'ordinateur |

!!! warning
    **Redémarrer** et **Éteindre** ont **Confirmer avant d'exécuter** activé — une boîte de dialogue vous demandera de confirmer avant toute action.

### Développement

Git Status · Git Log · Git Diff · Docker PS · Docker PS All · Docker Images · Docker Clean · Tail Syslog · Disk I/O · Python Version · Pip Outdated · Node Version · NPM Outdated · Listening Services

---

## Commencez par cliquer

Cliquez sur **Utilisation disque**. Une petite boîte de dialogue s'ouvre avec les informations de votre système de fichiers. Cliquez sur **Utilisation mémoire**. Essayez-en d'autres.

Vous ne pouvez rien casser en cliquant sur ces boutons — ils ne font que lire des informations. Les deux boutons qui font vraiment quelque chose (Redémarrer et Éteindre) demandent une confirmation en premier.

---

## Masquer les catégories dont vous n'avez pas besoin

Si vous ne faites pas de développement, la catégorie Développement n'est qu'un encombrement. Vous pouvez la masquer :

1. Faites un clic droit sur la pastille **Développement** dans la barre d'onglets
2. Cliquez sur **Masquer la catégorie**

L'onglet et tous ses boutons disparaissent de la vue. Ils ne sont pas supprimés — vous pouvez les faire réapparaître à tout moment via **Préférences → Catégories**.

---

## Personnaliser le nom ou la couleur d'un bouton

Les noms des boutons par défaut sont fonctionnels mais génériques. Vous pouvez les renommer ou les recolorer selon votre style.

!!! note
    La modification des boutons par défaut nécessite [RemoteX Pro](../pro.md). Dans la version gratuite, vous pouvez utiliser, masquer et supprimer les boutons par défaut, mais pas les modifier.

Avec Pro, faites un clic droit sur n'importe quel bouton → **Modifier** :

- Changez l'**Étiquette** en quelque chose de plus convivial (`Utilisation disque` → `Mon disque est-il plein ?`)
- Choisissez une **Couleur** pour faire ressortir les boutons importants
- Changez l'**Icône** pour quelque chose qui vous parle davantage

---

## Créer votre premier bouton personnalisé

Vous disposez de **3 boutons personnalisés gratuits**. En voici un facile pour commencer :

1. Appuyez sur `Ctrl+N` (ou cliquez sur **+**)
2. **Étiquette :** `Mon adresse IP`
3. **Commande :** `hostname -I`
4. **Mode d'exécution :** `Afficher la sortie`
5. Cliquez sur **Enregistrer**

Vous avez maintenant un moyen en un clic de voir votre adresse IP locale.

---

## Que faire si un bouton affiche une erreur ?

Certains boutons nécessitent des logiciels qui peuvent ne pas être installés :

- **Température** — nécessite `lm-sensors` (`sudo apt install lm-sensors`)
- Boutons **Docker** — nécessitent Docker installé
- Boutons Développement pour Python/Node — nécessitent ces environnements d'exécution

Si une commande échoue, une boîte de dialogue de sortie s'ouvre avec l'erreur exacte. Il s'agit généralement d'un paquet manquant — copiez le nom du paquet et installez-le.

---

## Aller plus loin avec RemoteX

Une fois à l'aise avec les boutons par défaut :

- [Créer des boutons personnalisés](../quick-start.md#3-créer-votre-premier-bouton-personnalisé) pour vos propres commandes fréquentes
- [Organiser avec des catégories](../reference/main-window.md#barre-de-catégories) pour regrouper les boutons liés
- [Ajuster la mise en page de la grille](../reference/preferences.md#boutons-par-ligne) pour s'adapter à votre écran
- Envisager [RemoteX Pro](../pro.md) lorsque vous souhaitez gérer un serveur distant
