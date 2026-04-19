# Licence et appareils

!!! tip "Pro"
    Une clé de licence est nécessaire pour activer [RemoteX Pro](../pro.md).

Chaque clé de licence autorise **3 activations simultanées** sur vos propres appareils (usage personnel uniquement).

Le compteur actuel est affiché dans **Préférences → Licence → Activations**.

---

## Activer sur un nouvel appareil

1. Ouvrez **Préférences** (`Ctrl+,`) sur l'appareil
2. Faites défiler jusqu'à la section **Licence**
3. Saisissez votre clé de licence et l'adresse e-mail utilisée lors de l'achat
4. Cliquez sur **Activer Pro**

Une connexion Internet est requise pour la première activation.

---

## Scénarios courants

### Jusqu'à 3 appareils (bureau + portable + serveur)

Activez sur chaque appareil normalement. Chaque activation consomme un slot.

| Appareil | Action | Slots utilisés |
|----------|--------|----------------|
| Bureau | Activer | 1 / 3 |
| Portable | Activer | 2 / 3 |
| Serveur maison | Activer | 3 / 3 |

### Remplacer un ordinateur (migration planifiée)

Vous souhaitez remplacer un ancien appareil par un nouveau.

1. Sur **l'ancien appareil**, ouvrez **Préférences → Licence → Désactiver** — cela libère un slot (3 → 2)
2. Configurez le nouvel appareil et installez RemoteX
3. Activez votre licence sur le nouvel appareil (2 → 3)

Résultat : même nombre de slots, aucun slot perdu.

### Réinstallation du système — avec désactivation préalable

Identique à la migration planifiée ci-dessus. Désactivez avant de réinstaller, puis réactivez ensuite. Le slot est libéré et réutilisé — votre compteur reste identique.

### Crash de l'ordinateur ou réinstallation sans désactivation préalable

!!! warning
    Réinstaller sans désactiver au préalable laisse un slot d'activation orphelin.
    L'ancien slot ne peut pas être libéré automatiquement — la machine n'existe plus pour envoyer une demande de désactivation.

Si vous atteignez la limite d'activations à cause d'un slot orphelin, **contactez le support** :

**[support@neurocontrarian.com](mailto:support@neurocontrarian.com)**

Indiquez les 4 premiers caractères de votre clé de licence. Nous libérerons manuellement le slot orphelin depuis notre tableau de bord.

!!! tip
    Ouvrez toujours **Préférences → Licence → Désactiver** avant de réinstaller votre système ou d'effacer un appareil.

### Désactivation accidentelle de la licence

Aucun problème. Réactivez simplement sur le même appareil — cela réutilise le même slot. Votre compteur d'activations n'augmente pas.

| Étape | Slots utilisés |
|-------|----------------|
| Avant la désactivation accidentelle | 3 / 3 |
| Après désactivation | 2 / 3 |
| Après réactivation sur le même appareil | 3 / 3 |

### Tenter d'activer sur un 4e appareil

Si vos 3 slots sont tous utilisés, l'activation échouera avec un message d'erreur.

**Option 1** — Libérer un slot volontairement : ouvrez RemoteX sur l'un de vos 3 appareils actifs, allez dans **Préférences → Licence → Désactiver**, puis activez sur le nouvel appareil.

**Option 2** — Si un slot est orphelin (ancien appareil inaccessible) : contactez le support à [support@neurocontrarian.com](mailto:support@neurocontrarian.com).

!!! note
    Le portail client LemonSqueezy ne permet **pas** de désactiver soi-même ses instances. Pour libérer un slot, vous devez utiliser le bouton Désactiver dans RemoteX, ou contacter le support.

---

## Politique de partage de clé

Chaque clé de licence est personnelle et non transférable. Lors de l'activation, RemoteX vérifie que l'adresse e-mail saisie correspond à celle de l'achat. Les clés détectées sur plus de 3 appareils simultanément seront révoquées sans remboursement.
