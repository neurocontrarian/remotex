# Politique de confidentialité

*Dernière mise à jour : avril 2026*

## Fournisseur

RemoteX est exploité par **neurocontrarian**, situé au Québec, Canada. Le traitement des paiements est assuré par [LemonSqueezy](https://www.lemonsqueezy.com), agissant en tant que Merchant of Record — ils sont responsables de toutes les données de paiement client.

L'auteur n'exploite aucun serveur collectant des données utilisateur : la validation de licence s'effectue directement entre votre machine et l'API de LemonSqueezy. L'auteur n'a accès à aucune information d'achat des utilisateurs au-delà des rapports de ventes agrégés fournis par LemonSqueezy.

**Contact pour toute question relative à la confidentialité :** [neurocontrarian@gmail.com](mailto:neurocontrarian@gmail.com)

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

Aucun de ces fichiers n'est transmis à un serveur. La clé de licence et les métadonnées d'activation sont stockées localement et utilisées uniquement lors des appels de validation vers LemonSqueezy.

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

## Modifications de cette politique

Nous nous réservons le droit de mettre à jour cette Politique de confidentialité à tout moment, à notre seule discrétion. Les modifications prennent effet dès leur publication sur cette page. La date « Dernière mise à jour » en haut reflète la révision la plus récente. Nous vous encourageons à consulter cette page régulièrement.

## Contact

Pour toute question ou pour exercer vos droits de protection des données : [neurocontrarian@gmail.com](mailto:neurocontrarian@gmail.com)
