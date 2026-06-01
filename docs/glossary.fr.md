# Glossaire

Certains mots de ce wiki vous échappent ? Les voici en langage simple.

**Commande**
: Une ligne de texte qui dit à l'ordinateur quoi faire — par ex. `df -h` affiche l'espace disque libre. Commandeck exécute une commande pour vous quand vous cliquez un bouton, pour ne pas avoir à la taper.

**Bouton (tuile)**
: Un carré de la grille Commandeck. Chaque bouton contient une commande et l'exécute au clic.

**Shell**
: Le programme qui lit et exécute les commandes. Sous Linux et macOS c'est généralement `bash` ou `zsh` ; sous Windows c'est **PowerShell**. Commandeck utilise automatiquement le bon selon votre système.

**Terminal**
: La fenêtre de texte noire où l'on tape normalement les commandes. Commandeck existe justement pour vous en passer — même si un bouton peut en ouvrir un si vous choisissez le mode « Ouvrir dans un terminal ».

**Catégorie**
: Une étiquette qui regroupe des boutons liés (par ex. *Réseau*, *Matériel*). Les catégories apparaissent en onglets au-dessus de la grille pour filtrer l'affichage.

**SSH** *(Pro)*
: Une façon sécurisée d'exécuter des commandes sur un autre ordinateur via le réseau — par exemple gérer un serveur maison depuis votre portable. Commandeck utilise SSH pour envoyer la commande d'un bouton à une machine distante.

**Machine** *(Pro)*
: Un ordinateur distant que vous avez ajouté à Commandeck (adresse, utilisateur, clé SSH). Les boutons peuvent cibler une ou plusieurs machines.

**sudo / exécuter en tant qu'utilisateur**
: `sudo` exécute une commande avec les droits d'administrateur ; *exécuter en tant qu'utilisateur* l'exécute sous un compte précis (par ex. un compte de service comme `www-data`). Commandeck peut le faire pour vous via un [profil d'exécution](reference/execution-profiles.fr.md).

**Profil d'exécution** *(Pro)*
: Un ensemble enregistré de « conditions d'exécution » — quel utilisateur et quel dossier — réutilisable sur plusieurs boutons. Voir [Profils d'exécution](reference/execution-profiles.fr.md).

**Sortie**
: Ce qu'une commande renvoie (par ex. les chiffres d'utilisation du disque). Un bouton peut l'afficher dans une fenêtre, s'exécuter en silence, ou ouvrir un terminal.

**AppImage**
: Une application Linux en un seul fichier — téléchargez-la, rendez-la exécutable, lancez-la. Aucune installation, rien à configurer au niveau système.

**MCP** *(Pro)*
: Le pont qui permet à un assistant IA de lire et gérer vos boutons. Voir [Intégration IA](pro/mcp.fr.md).

**Gratuit vs Pro**
: La version **Gratuite** exécute des commandes locales illimitées avec jusqu'à 3 boutons personnalisés. **Pro** ajoute les machines SSH, les boutons multi-machines, les thèmes, les profils, la sauvegarde et l'intégration IA — avec un essai gratuit de 14 jours.
