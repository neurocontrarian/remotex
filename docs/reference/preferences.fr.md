# Préférences

Ouvrez les Préférences depuis le menu hamburger ou avec `Ctrl+,`.

Les paramètres sont enregistrés immédiatement lorsque vous les modifiez — il n'y a pas de bouton Enregistrer.

---

## Général

![Préférences — Général et Mise en page](../assets/preferences-general.png)

### Langue

Sélectionne la langue de l'interface. RemoteX prend en charge 12 langues :

| Code | Langue |
|------|--------|
| Système | Suivre la locale du bureau (par défaut) |
| en | Anglais |
| fr | Français |
| de | Allemand |
| es | Espagnol |
| it | Italien |
| pt | Portugais |
| ru | Russe |
| ko | Coréen |
| ja | Japonais |
| zh | Chinois (simplifié) |
| ar | Arabe |
| hi | Hindi |

!!! note
    Un changement de langue prend effet après le redémarrage de RemoteX. Une notification toast vous le rappelle.

### Délai d'expiration des commandes

La durée maximale (en secondes) d'attente de la fin d'une commande avant annulation. Par défaut : **30 secondes**.

Augmentez cette valeur pour les commandes censées prendre du temps (copies de grands fichiers, mises à jour système). Diminuez-la pour échouer rapidement sur des machines inaccessibles.

### Boutons par ligne

Le nombre de colonnes dans la grille de boutons. Plage : 1–20. Appliqué en direct sans redémarrage.

Une valeur de 4 (la valeur par défaut) fonctionne bien pour des boutons de taille moyenne sur un écran 1080p typique.

### Confirmer avant d'exécuter par défaut

Lorsque cette option est activée, la case **Confirmer avant d'exécuter** dans l'éditeur de bouton est pré-cochée pour chaque nouveau bouton créé.

N'affecte pas les boutons existants.

---

## Apparence des boutons

![Préférences — Apparence des boutons](../assets/preferences-appearance.png)

### Taille des boutons

Définit la taille de toutes les tuiles de boutons globalement.

| Taille | Dimensions de la tuile | Taille de l'icône |
|--------|------------------------|-------------------|
| Petite | 80 × 80 px | 20 px |
| Moyenne | 120 × 120 px | 32 px |
| Grande | 160 × 160 px | 48 px |

### Thème des boutons

!!! tip "Fonctionnalité Pro"
    Les thèmes de boutons nécessitent [RemoteX Pro](../pro.md). Dans la version gratuite, cette option est verrouillée sur **Gras** (thème système par défaut).

Applique un style visuel à toutes les tuiles de boutons. Consultez [Thèmes](../pro/themes.md) pour une description complète et des captures d'écran de chaque option.

| Thème | Style |
|-------|-------|
| Gras | Tuiles colorées pleines avec un fort contraste (par défaut) |
| Phone | Tuiles plates compactes, évoquant un clavier de téléphone |
| Neon | Fond sombre avec des bordures lumineuses de la couleur d'accent |
| Retro | Style monochrome inspiré du terminal avec des lignes de balayage |

---

## Intégration bureau

![Préférences — Intégration bureau](../assets/preferences-desktop.png)


### Toujours au premier plan

Lorsque cette option est activée, la fenêtre RemoteX flotte au-dessus de toutes les autres fenêtres. Nécessite `wmctrl`, inclus dans les dépendances requises (voir les instructions d'installation). Si le paquet est absent de votre système :

```bash
sudo apt install wmctrl
```

Ce paramètre est également accessible depuis le menu hamburger comme raccourci.

### Lancer au démarrage de session

Lorsque cette option est activée, RemoteX démarre automatiquement à la connexion à votre bureau. Cela crée un fichier `.desktop` dans `~/.config/autostart/remotex.desktop`.

La désactivation supprime le fichier de démarrage automatique.

### Autoriser l'accès MCP

Active le serveur MCP (Model Context Protocol) intégré. Lorsqu'il est actif, un assistant IA compatible (Claude Desktop, Cursor, etc.) peut lire et gérer vos boutons.

Désactivé par défaut. Consultez [Intégration IA (MCP)](../pro/mcp.fr.md) pour les instructions de configuration.

!!! warning
    Lorsque l'accès MCP est activé, votre assistant IA peut créer, modifier et supprimer des boutons. Désactivez cette option lorsque vous ne l'utilisez pas.

---

## Catégories

![Préférences — Catégories](../assets/preferences-categories.png)

Liste toutes les catégories qui existent actuellement dans votre configuration de boutons. Chaque ligne possède une option à bascule :

- **Activée** — la pastille de catégorie est visible dans la barre de catégories et ses boutons apparaissent dans la grille
- **Désactivée** — la catégorie et ses boutons sont masqués de la grille (mais pas supprimés)

C'est la façon de restaurer une catégorie après l'avoir masquée avec clic droit → **Masquer la catégorie**.

La liste se met à jour automatiquement lorsque vous ajoutez ou supprimez des catégories.

---

## Profils d'exécution *(Pro)*

Gérez les contextes d'exécution nommés depuis le menu hamburger → **Gérer les profils** (accessible aussi depuis cette section). Chaque profil regroupe :

- **Nom du profil** — un libellé court et descriptif (par ex. `En tant que www-data dans /var/www`)
- **Exécuter en tant que** — l'utilisateur cible : utilisateur courant (sans sudo), root, ou un nom d'utilisateur personnalisé
- **Répertoire de travail** — le répertoire dans lequel effectuer un `cd` avant d'exécuter la commande
- **Mot de passe sudo** — stocké localement avec un encodage propre à la machine ; transmis automatiquement à `sudo -S` à l'exécution, sans invite dans le terminal

Assignez un profil à un bouton dans l'[Éditeur de bouton](button-editor.md#profil-dexécution) pour appliquer ses paramètres.

!!! tip "Fonctionnalité Pro"
    Les profils d'exécution nécessitent [RemoteX Pro](../pro.md).

---

## Licence

![Préférences — Licence](../assets/preferences-license.png)

Gère votre licence RemoteX Pro.

### Activation

1. Achetez une licence sur la [page RemoteX Pro](../pro.md)
2. Collez votre clé de licence dans le champ
3. Cliquez sur **Activer Pro**

Une connexion internet est nécessaire pour l'activation initiale.

### Affichage de la licence active

Lorsqu'une licence valide est active, cette section affiche :

- **Type de licence** — Annuelle ou À vie
- **Date d'expiration** — pour les licences annuelles (non affichée pour les licences à vie)
- **Statut** — Active, ou un avertissement si l'expiration est dans 30 jours

### Renouvellement (licence annuelle)

Cliquez sur **Renouveler la licence** pour revalider votre clé après l'achat d'un renouvellement. Nécessite une connexion internet.

### Désactivation

Cliquez sur **Désactiver la licence** pour retirer la licence Pro de cet appareil. Les limites de la version gratuite s'appliquent immédiatement.

Vos boutons et machines ne sont pas supprimés — les boutons personnalisés au-delà de 3 sont temporairement masqués jusqu'à la réactivation.
