# RemoteX Pro

## Gratuit vs Pro

| | Gratuit | Pro |
|--|---------|-----|
| Exécution locale | Illimitée | Illimitée |
| Boutons par défaut (utilisation) | Illimitée | Illimitée |
| Boutons par défaut (modification) | Lecture seule | Modifiables |
| Boutons personnalisés | **3** | Illimités |
| Machines SSH | — | Illimitées |
| Boutons multi-machines | — | ✓ |
| Sélection multiple + actions de groupe | — | ✓ |
| Thèmes de boutons (Bold, Phone, Neon, Retro…) | — | ✓ |
| Thème CSS personnalisé | — | ✓ |
| Profils d'exécution | — | ✓ |
| Sauvegarde / restauration de la config | — | ✓ |

!!! note
    Les boutons par défaut (Linux Essentials, Développement) sont toujours **visibles, exécutables et supprimables** dans la version gratuite. Seule la modification de leurs paramètres nécessite Pro.

## Tarifs

- **20 $ / an** — licence annuelle, renouvelez pour conserver l'accès Pro
- **40 $ à vie** — achat unique, sans renouvellement

[Obtenir une licence →](https://neurocontrarian.lemonsqueezy.com/checkout/buy/f2b9451a-588d-49c2-b1ed-1afe21ffd9e2){ .md-button .md-button--primary }

## Activer votre licence

1. Ouvrez les **Préférences** (`Ctrl+,`)
2. Faites défiler jusqu'à la section **Licence**
3. Collez votre clé de licence dans le champ
4. Cliquez sur **Activer Pro**

Une connexion internet est nécessaire pour l'activation initiale.

## Licence annuelle — renouvellement

Une licence annuelle expire 365 jours après l'activation. RemoteX affiche un avertissement toast 30 jours avant l'expiration.

Après expiration, les limites de la version gratuite s'appliquent à nouveau — vos boutons et machines ne sont **pas supprimés**, mais les boutons personnalisés au-delà de 3 sont temporairement masqués.

Renouvelez depuis **Préférences → Licence → Renouveler la licence**.

## Désactivation

Pour retirer la licence d'un appareil : **Préférences → Licence → Désactiver la licence**.

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
