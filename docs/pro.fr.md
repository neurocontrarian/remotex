# RemoteX Pro

RemoteX existe en deux versions : **Gratuite** (open source, exécution locale uniquement) et **Pro** (propriétaire, avec SSH et intégration IA).

## Gratuit vs Pro

| | Gratuit | Pro |
|--|---------|-----|
| Exécution locale | Illimitée | Illimitée |
| Boutons personnalisés | Illimités | Illimités |
| Boutons par défaut | Visibles, exécutables, supprimables | Modifiables |
| Machines SSH | — | Illimitées |
| Boutons multi-machines | — | ✓ |
| Sélection multiple + actions de groupe | — | ✓ |
| Thèmes de boutons (Bold, Phone, Neon, Retro…) | — | ✓ |
| Thème CSS personnalisé | — | ✓ |
| Profils d'exécution | — | ✓ |
| Sauvegarde / restauration de la config | — | ✓ |
| Serveur MCP (intégration IA) | — | ✓ |
| Exécution de boutons par l'IA | — | ✓ |

!!! note
    Les versions Gratuite et Pro sont des **téléchargements séparés**, pas le même binaire avec une clé de déverrouillage. La version Gratuite ne contient aucun code Pro.

## Tarif

**29 $ / an** — licence annuelle, **renouvelée automatiquement** à 29 $ chaque année sauf annulation.

Vous pouvez annuler à tout moment depuis le portail client LemonSqueezy (le lien se trouve dans votre e-mail d'achat). L'annulation empêche le prochain renouvellement — votre période en cours continue jusqu'à sa date d'expiration, et les fonctionnalités Pro restent disponibles jusque-là.

Une option à vie pourra être proposée plus tard sous forme d'événement limité. Au lancement, seule la licence annuelle est disponible.

[Obtenir une licence →](https://neurocontrarian.lemonsqueezy.com/checkout/buy/9c16845a-8ab6-4a36-b8da-9874d9d64f33){ .md-button .md-button--primary }

## Essai gratuit de 14 jours

La version Pro inclut un **essai automatique de 14 jours** qui démarre au premier lancement. Pas de clé de licence, pas de paiement, pas de saisie d'email — toutes les fonctionnalités Pro sont disponibles immédiatement.

Quelques jours avant la fin de l'essai, RemoteX affiche une offre intégrée avec un code de réduction. Après le 14ᵉ jour, les fonctionnalités Pro deviennent en lecture seule (grisées) — vos boutons, machines et préférences ne sont **jamais supprimés**.

Pour continuer à utiliser Pro, activez une licence depuis **Préférences → Licence**.

## Activer votre licence

1. Ouvrez les **Préférences** (`Ctrl+,`)
2. Faites défiler jusqu'à la section **Licence**
3. Saisissez l'adresse email utilisée pour l'achat
4. Collez votre clé de licence
5. Cliquez sur **Activer Pro**

Une connexion internet est nécessaire pour l'activation initiale. La licence est ensuite validée hors ligne quotidiennement.

## Renouvellement annuel

Une licence annuelle expire 365 jours après l'activation. RemoteX affiche un avertissement 30 jours avant l'expiration.

Après expiration, les limites de la version Gratuite s'appliquent à nouveau — vos boutons et machines ne sont **pas supprimés**, mais les fonctionnalités Pro (SSH, MCP, sélection multiple, thèmes, etc.) deviennent indisponibles jusqu'au renouvellement.

Renouvelez depuis **Préférences → Licence → Renouveler la licence**.

## Désactivation

Pour retirer la licence d'un appareil : **Préférences → Licence → Désactiver la licence**.

Cela libère un emplacement d'activation pour utiliser la même clé sur un autre appareil. Votre licence Pro autorise jusqu'à 3 activations simultanées sur vos appareils personnels — voir [Licence & Appareils](pro/license-devices.fr.md) pour plus de détails.

Les limites de la version Gratuite s'appliquent immédiatement après la désactivation. Vos boutons ne sont pas supprimés ; les fonctionnalités Pro sont restaurées lors de la réactivation.

## Profils d'exécution *(Pro)*

Créez des contextes d'exécution réutilisables combinant un utilisateur cible, un répertoire de travail et un mot de passe sudo dans un seul profil nommé.

Assignez un profil à n'importe quel bouton — lors de l'exécution, la commande s'exécute sous l'utilisateur spécifié dans le répertoire spécifié, avec le mot de passe sudo transmis automatiquement (aucune invite dans le terminal).

Les profils fonctionnent en exécution locale et distante (SSH), y compris en mode **Ouvrir dans le terminal**.

Gérez les profils depuis le menu hamburger → **Gérer les profils**.

---

## Sauvegarde et restauration *(Pro)*

Exportez et importez votre configuration complète depuis les **Préférences** :

- **Sauvegarde boutons & paramètres** — exporte les boutons et les préférences dans un fichier `.rxbackup`
- **Sauvegarde des machines** — exporte les définitions des machines SSH dans un fichier `.rxmachines` (les clés privées SSH ne sont jamais incluses)

Restaurez depuis la même section des Préférences. L'importation des boutons fusionne avec les boutons par défaut existants — les nouveaux boutons par défaut ajoutés ultérieurement ne sont jamais perdus.

---

## Intégration IA *(Pro)*

Le serveur MCP permet aux assistants IA comme Claude, Cursor ou Open WebUI de lire, modifier et exécuter vos boutons via une connexion sécurisée unique. Voir [Intégration IA (MCP)](pro/mcp.fr.md) pour la configuration complète et les détails de sécurité.
