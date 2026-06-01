# Sécurité & fonctionnement interne

🔰 **En clair :** Commandeck exécute des commandes que *vous* écrivez et cliquez, sur vos propres machines. Il ne stocke jamais de mot de passe en clair, n'ouvre aucun port réseau en usage normal, et demande confirmation pour tout ce que vous marquez comme sensible. Cette page détaille les garde-fous — utile pour un sysadmin qui décide s'il peut faire confiance à l'outil.

## Vos commandes, visibles et modifiables

La commande de chaque bouton est affichée en clair dans l'[éditeur de bouton](button-editor.fr.md). Rien n'est caché ni obscurci — ce que vous voyez est exactement ce qui s'exécute. Commandeck ne réécrit jamais vos commandes (il les enveloppe seulement du `cd` / `sudo -u` d'un profil quand vous le demandez).

## SSH : des clés, pas des mots de passe

Les connexions SSH (Pro) utilisent **uniquement l'authentification par clé** — Commandeck ne stocke jamais de mot de passe de connexion SSH.

- Les connexions utilisent Paramiko avec une politique stricte de clés d'hôte et votre `known_hosts`.
- **Premier contact (TOFU) :** la première fois que vous joignez un nouvel hôte, Commandeck affiche l'empreinte de sa clé et vous demande de la confirmer — la même vérification que `ssh` en ligne de commande, mais dans une boîte de dialogue.
- Les clés protégées par phrase secrète nécessitent un `ssh-agent` actif ; Commandeck affiche une erreur claire si l'agent est verrouillé plutôt que d'échouer silencieusement.
- La copie de votre clé publique vers un serveur passe par SFTP — aucune commande shell n'est construite à partir de votre saisie, donc pas de surface d'injection.

## Mots de passe sudo

Le [mot de passe sudo](execution-profiles.fr.md) facultatif d'un profil n'est **jamais stocké en clair**. Il est encodé en XOR avec l'identifiant unique de votre machine et écrit dans la config locale uniquement. Comme la clé est l'ID machine, la valeur encodée n'est **pas transférable** — copier la config sur une autre machine ne révèle ni ne réutilise le mot de passe. À l'exécution, il est passé à `sudo -S` pour éviter toute invite dans un terminal.

## Confirmation par bouton

N'importe quel bouton peut exiger **Demander confirmation avant l'exécution** (éditeur → Comportement). Activé, Commandeck affiche la commande exacte et attend votre accord avant d'exécuter — recommandé pour les redémarrages, suppressions, et tout ce qui touche à `sudo`.

## Accès IA / MCP (Pro)

Le [serveur MCP](../pro/mcp.fr.md) permet à un assistant IA de lire et modifier vos boutons. Il est **désactivé par défaut** et protégé :

- **Lire/modifier** nécessite d'activer *Autoriser l'accès MCP* dans les Préférences.
- **Exécuter** un bouton par l'IA nécessite **trois** autorisations indépendantes — un interrupteur global, un drapeau par bouton, et (pour les boutons sensibles) une confirmation. Si l'une est désactivée, l'exécution est bloquée.
- Chaque exécution déclenchée par l'IA est inscrite dans un journal d'audit (`<config>/.mcp_executions.log`) avec horodatage, bouton, cible, code de retour et durée.
- Le serveur utilise stdio (aucun port réseau) quand il est lancé par un client IA de bureau. Seul le pont mcpo (pour Open WebUI) ouvre un port HTTP local — gardez-le sur votre réseau local, derrière votre pare-feu.

## Modèle de menace

Commandeck est un **outil de bureau mono-utilisateur**. Il suppose que la personne au clavier a le droit d'exécuter des commandes sur ses propres machines — ce n'est pas une frontière multi-locataire ni de séparation de privilèges. Ses garde-fous servent à éviter les *accidents* (lancer la mauvaise chose, fuiter un secret dans une synchro, une IA qui agit sans accord), pas à se défendre contre un utilisateur local hostile qui contrôle déjà votre compte.
