# Politique de confidentialité

*Dernière mise à jour : avril 2026*

## Données collectées

RemoteX collecte un minimum de données, strictement nécessaires à la validation de licence.

### Lors de l'achat (via LemonSqueezy)

Votre adresse e-mail et vos informations de paiement sont collectées par [LemonSqueezy](https://www.lemonsqueezy.com), notre prestataire de paiement. Nous recevons uniquement votre adresse e-mail à des fins de validation de licence. Nous ne recevons ni ne stockons vos coordonnées bancaires.

### Lors de l'activation de la licence

Lorsque vous activez une licence Pro, les données suivantes sont transmises à l'API de LemonSqueezy :

- Votre clé de licence
- Un identifiant d'appareil anonyme (`/etc/machine-id`, haché — non lié à une identité personnelle)
- Le nom de l'activation (votre nom d'hôte, facultatif)

Ces données servent uniquement à vérifier la validité de votre licence et à gérer vos emplacements d'activation (max 3 appareils).

### Stocké localement sur votre machine

RemoteX stocke les fichiers suivants dans `~/.config/remotex/` :

- `buttons.toml` — votre configuration de boutons
- `machines.toml` — vos définitions de machines SSH (sans clés privées)
- `profiles.toml` — vos profils d'exécution (les mots de passe sudo sont encodés avec une clé propre à la machine, jamais transmis)
- `license.key` — votre clé de licence et métadonnées d'activation

Aucun de ces fichiers n'est transmis à un serveur, à l'exception de la clé de licence lors des appels de validation.

## Ce que nous ne collectons pas

- Nous ne collectons pas de données analytiques ni d'utilisation
- Nous ne suivons pas les commandes que vous exécutez
- Nous n'avons pas accès à vos identifiants SSH ni à vos clés privées
- Nous n'utilisons pas de cookies ni de suivi web

## Services tiers

La validation de licence est gérée par [LemonSqueezy](https://www.lemonsqueezy.com). Leur politique de confidentialité s'applique aux données qu'ils traitent. Les appels de validation sont effectués lors de l'activation et périodiquement (quotidiennement) lorsque l'application est en cours d'exécution.

## Conservation des données

Nous ne stockons aucune donnée personnelle sur nos serveurs. Toute votre configuration reste sur votre machine locale.

## Vos droits

Vous pouvez demander la suppression de votre compte et des données associées en nous contactant. La désactivation de votre licence supprime l'enregistrement d'activation d'appareil des serveurs de LemonSqueezy.

## Contact

[flelard@gmail.com](mailto:flelard@gmail.com)
