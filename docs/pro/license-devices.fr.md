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

### Réinstallation du système — sans désactivation préalable

Après la réinstallation, votre ancien slot d'activation existe toujours chez LemonSqueezy (l'ancien identifiant machine est toujours enregistré). L'activation sur le système fraîchement installé consomme un nouveau slot.

Si vous atteignez la limite de 3 appareils à cause de ce slot orphelin :

1. Ouvrez RemoteX sur un autre appareil encore activé et désactivez via **Préférences → Licence → Désactiver** pour libérer un slot, puis réessayez
2. Si vous n'avez aucun autre appareil actif pour désactiver, [contactez le support](mailto:neurocontrarian@gmail.com) — nous libérerons le slot orphelin manuellement depuis le tableau de bord

!!! warning "Désactivez avant de réinstaller"
    Pour éviter cette situation, ouvrez toujours **Préférences → Licence → Désactiver** avant de réinstaller ou de formater votre système d'exploitation.

### Désactivation accidentelle de la licence

Aucun problème. Réactivez simplement sur le même appareil — cela réutilise le même slot. Votre compteur d'activations n'augmente pas.

| Étape | Slots utilisés |
|-------|----------------|
| Avant la désactivation accidentelle | 3 / 3 |
| Après désactivation | 2 / 3 |
| Après réactivation sur le même appareil | 3 / 3 |

### Tenter d'activer sur un 4e appareil

Si vos 3 slots sont tous utilisés, l'activation échouera avec un message d'erreur.

Ouvrez RemoteX sur l'un de vos 3 appareils actifs, allez dans **Préférences → Licence → Désactiver**, puis activez sur le nouvel appareil.

!!! note
    Le portail client LemonSqueezy ne permet **pas** de désactiver soi-même ses instances. Pour libérer un slot, utilisez le bouton **Désactiver** dans RemoteX sur l'un de vos appareils actifs.

---

## Politique de partage de clé

Chaque clé de licence est personnelle et non transférable. Lors de l'activation, RemoteX vérifie que l'adresse e-mail saisie correspond à celle de l'achat. Les clés détectées sur plus de 3 appareils simultanément seront révoquées sans remboursement.
