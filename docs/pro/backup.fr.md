# Sauvegarde & Restauration

!!! tip "Fonctionnalité Pro"
    La sauvegarde et la restauration de la configuration nécessitent [RemoteX Pro](../pro.md).

RemoteX propose deux formats d'export distincts, intentionnellement séparés pour des raisons de sécurité.

Accédez aux deux depuis **Préférences → (faire défiler vers le bas)**.

---

## Sauvegarde boutons & paramètres — `.rxbackup`

Cette archive contient :

- `buttons.toml` — tous vos boutons et leur configuration
- `gsettings.json` — tous les paramètres des Préférences (colonnes, taille des boutons, thème, langue, etc.)

### Quand l'utiliser

- Avant un changement majeur (suppression de nombreux boutons, réorganisation des catégories)
- Lors de la migration de RemoteX vers un nouvel ordinateur
- Comme instantané périodique de votre bibliothèque de boutons

### Export

Cliquez sur **Exporter Boutons & Paramètres**. Un sélecteur de fichier s'ouvre. Choisissez un emplacement et enregistrez le fichier `.rxbackup`.

### Import

Cliquez sur **Importer Boutons & Paramètres**. Sélectionnez un fichier `.rxbackup`. RemoteX **fusionne** les boutons importés avec vos boutons actuels — il n'efface pas votre configuration existante au préalable.

!!! note
    Les boutons par défaut (Linux Essentials, Développement) initialisés par RemoteX ne sont jamais écrasés lors de l'import — les nouveaux boutons par défaut ajoutés dans une version ultérieure sont préservés.

---

## Sauvegarde des machines — `.rxmachines`

Cette archive contient :

- `machines.toml` — toutes les définitions de machines SSH (nom, hôte, utilisateur, port, chemin de la clé, icône)

### Ce qui n'est PAS inclus

Les **clés privées** SSH ne sont jamais exportées. L'archive ne stocke que le chemin vers le fichier de clé (`~/.ssh/id_ed25519`), pas la clé elle-même.

!!! warning
    Le fichier `.rxmachines` contient des noms d'hôtes, adresses IP, noms d'utilisateurs SSH et numéros de port. Traitez-le comme tout fichier de configuration réseau — ne le partagez pas publiquement et ne le stockez pas dans un emplacement public non chiffré.

### Quand l'utiliser

- Lors de la configuration de RemoteX sur un deuxième ordinateur (vous devrez quand même copier les clés SSH séparément)
- Comme archive de la configuration de votre infrastructure serveur

### Export

Cliquez sur **Exporter les machines**. Choisissez un emplacement et enregistrez le fichier `.rxmachines`.

### Import

Cliquez sur **Importer les machines**. Sélectionnez un fichier `.rxmachines`. Les machines sont fusionnées avec les machines existantes. Les doublons (même combinaison hôte + utilisateur) sont ignorés.

---

## Restauration sur un nouvel ordinateur

Liste de contrôle pour une migration complète :

1. Installez RemoteX sur la nouvelle machine
2. Copiez vos clés privées SSH dans `~/.ssh/` sur la nouvelle machine (utilisez `scp` ou une clé USB — gardez-les sécurisées)
3. Activez votre licence Pro dans les Préférences
4. Importez le fichier `.rxbackup` pour restaurer les boutons et les paramètres
5. Importez le fichier `.rxmachines` pour restaurer les définitions des machines
6. Testez chaque connexion machine depuis **Menu → Gérer les machines → (sélectionner la machine) → Tester**
