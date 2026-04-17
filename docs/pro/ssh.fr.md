# SSH & Multi-machines

!!! tip "Fonctionnalité Pro"
    Les machines SSH et les boutons multi-machines nécessitent [RemoteX Pro](../pro.md).

Cette page couvre le workflow Pro spécifique pour SSH : ajouter des machines, les assigner à des boutons et utiliser le sélecteur de machine. Pour une référence complète champ par champ de la boîte de dialogue Ajouter une machine, consultez [Machines SSH](../reference/ssh-machines.md).

---

## Ajouter votre première machine

1. Ouvrez **Menu → Gérer les machines**
2. Cliquez sur **+** pour ouvrir la boîte de dialogue Ajouter une machine
3. Renseignez le nom de la machine, l'hôte, l'utilisateur SSH et le chemin de la clé
4. Cliquez sur **Tester** pour vérifier la connexion
5. Cliquez sur **Enregistrer**

La machine est maintenant disponible dans chaque éditeur de bouton.

Pour les instructions de configuration des clés SSH (génération d'une paire de clés et copie sur le serveur), consultez [Configuration des clés SSH](../reference/ssh-machines.md#configuration-des-clés-ssh).

---

## Assigner une machine à un bouton

Ouvrez l'éditeur de bouton (créez un nouveau bouton ou faites un clic droit sur un bouton existant → **Modifier**).

Dans la section **Machines cibles** :

- Désactivez **Local** si vous souhaitez uniquement la machine distante
- Activez la ou les machines souhaitées

Cliquez sur **Enregistrer**. L'infobulle du bouton affiche désormais le nom de la machine cible.

---

## Boutons à machine unique

Lorsqu'une seule cible est activée, la commande s'exécute immédiatement sur cette cible — sans sélecteur, sans clic supplémentaire. C'est la configuration la plus courante.

---

## Boutons multi-machines

Activez deux cibles ou plus et le bouton devient un bouton multi-machines. Chaque clic ouvre le [sélecteur de machine](../reference/ssh-machines.md#le-sélecteur-de-machine).

Le sélecteur liste chaque cible activée par nom et icône. Sélectionnez-en une et cliquez sur **Exécuter**.

### Mélanger Local et distant

Activez **Local** avec une ou plusieurs machines SSH pour inclure votre propre ordinateur comme option dans le sélecteur. Utile pour les scripts qui fonctionnent de façon identique dans les deux environnements.

### Raccourci "Toutes les machines"

Dans l'éditeur de bouton, l'option **Toutes les machines** en haut de la liste des machines sélectionne toutes les machines configurées en même temps. C'est pratique lorsque vous souhaitez qu'une commande comme `df -h` soit disponible sur toute votre flotte sans cocher chaque case individuellement.

---

## Patterns pratiques

### La même commande, plusieurs serveurs

Créez un bouton avec toutes les machines cibles activées. Le sélecteur vous permet de choisir quel serveur interroger à chaque fois.

### Commandes parallèles sur plusieurs serveurs

Les boutons multi-machines s'exécutent sur une machine par clic (via le sélecteur). Pour une véritable exécution parallèle sur plusieurs serveurs, ouvrez le bouton rapidement pour chaque machine en succession, ou utilisez un script shell qui gère les appels SSH directement.

### Bascule Local + distant

Un bouton avec Local et une machine serveur activés est utile pour les tests : exécutez d'abord la commande localement pour vérifier qu'elle fonctionne, puis choisissez le serveur pour déployer.

---

## Modes de sortie

Les trois modes d'exécution fonctionnent via SSH. Pour les sessions SSH interactives, utilisez **Ouvrir dans le terminal** — RemoteX génère automatiquement la bonne invocation `ssh -t`.

Consultez [Modes de sortie via SSH](../reference/ssh-machines.md#modes-de-sortie-via-ssh) pour la comparaison complète.
