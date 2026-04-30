# Activer votre licence

Bienvenue dans RemoteX Pro ! Ce guide vous accompagne pour activer votre licence sur votre premier appareil.

!!! tip "Ce dont vous avez besoin"
    - Votre **clé de licence** (envoyée dans l'email d'achat LemonSqueezy)
    - L'**adresse email** utilisée lors de l'achat
    - Une **connexion internet** (uniquement pour la première activation)

---

## Activation pas à pas

1. **Ouvrez RemoteX** — assurez-vous d'utiliser la version **Pro**, pas la version Free. ([Quelle est la différence ?](../pro.fr.md#free-vs-pro))

2. **Ouvrez les Préférences** avec `Ctrl + ,` ou via le menu burger → *Préférences*.

3. **Descendez jusqu'à la section *Licence*.**

    ![Section Licence dans les Préférences](../assets/license-section.png)

4. **Collez votre clé de licence** dans le champ *Clé de licence*.

5. **Saisissez l'email** utilisé à l'achat dans le champ *Email*.

    !!! warning "L'email doit correspondre exactement"
        Nous comparons ce que vous tapez à l'email enregistré chez LemonSqueezy pour cet achat. En cas de différence, l'activation est refusée — aucune activation n'est consommée.

6. Cliquez sur **Activer Pro**.

7. En quelques secondes, la boîte de dialogue se met à jour et affiche :
    - Le **type** de licence (Annuelle)
    - La **date d'expiration**
    - Le **nombre d'activations** (ex. *1 / 3*)

C'est tout — toutes les fonctionnalités Pro sont maintenant déverrouillées. Machines SSH, boutons multi-machines, thèmes, sauvegarde, serveur MCP, tout est disponible.

---

## Ce qui se passe ensuite

| Quand | Ce qui se passe |
|---|---|
| Juste après l'activation | Toutes les fonctionnalités Pro sont déverrouillées immédiatement |
| Toutes les 24 heures | RemoteX revalide silencieusement votre licence en ligne (pas d'UI, aucun ralentissement) |
| 30 jours avant l'expiration | Un toast prévient que votre abonnement va être renouvelé |
| Jour de l'expiration | LemonSqueezy renouvelle automatiquement l'abonnement — rien à faire |
| Si le renouvellement échoue | Une période de grâce de 3 jours s'applique avant le verrouillage des fonctionnalités Pro |

Si votre abonnement expire, **vos données ne sont jamais supprimées**. Boutons, machines, réglages — tout est conservé. Réactivez quand vous voulez et tout revient.

---

## En cas de problème

### *« Cette clé est enregistrée pour un autre email. »*

L'email que vous avez tapé ne correspond pas à celui de l'achat LemonSqueezy. Vérifiez l'email du reçu LemonSqueezy et utilisez cette adresse exacte (la casse n'importe pas, mais les fautes de frappe oui).

### *« Vous avez atteint la limite de 3 activations. »*

Vous avez utilisé les 3 emplacements d'activation de cette licence. Ouvrez RemoteX sur un de vos appareils actifs, allez dans **Préférences → Licence → Désactiver**, puis revenez ici pour activer.

Si vous n'avez plus accès à un appareil précédemment activé (laptop perdu, OS réinstallé sans désactiver, etc.), [contactez le support](mailto:neurocontrarian@gmail.com) — nous libérerons l'emplacement orphelin depuis le tableau de bord.

Voir le guide complet [Licence et appareils](license-devices.fr.md) pour tous les cas de figure.

### *« Erreur réseau — impossible de joindre le serveur de licences. »*

La première activation **nécessite** une connexion internet (nous vérifions la clé auprès de LemonSqueezy). Assurez-vous que RemoteX peut joindre `api.lemonsqueezy.com` — les proxies d'entreprise et pare-feu stricts peuvent le bloquer.

Après la première activation, RemoteX fonctionne hors-ligne. Nous revalidons seulement une fois toutes les 24 heures, avec 3 jours de grâce si le réseau est coupé.

### *Je ne vois pas de section « Licence » dans les Préférences*

Vous utilisez la version **Free**. La version Free n'a pas de système de licence — il n'y a rien à activer. Pour utiliser Pro, [téléchargez la version Pro](../pro.fr.md#téléchargement) et lancez-la à la place. Vos boutons, machines et réglages seront repris automatiquement (même répertoire de configuration).

---

## Pour aller plus loin

- **[Ajouter votre première machine SSH](../ssh.md)** — la fonction Pro par laquelle la plupart des gens commencent
- **[Créer un bouton multi-machines](../buttons.md#boutons-multi-machines)** — lancer une commande sur tout un parc
- **[Licence et appareils](license-devices.fr.md)** — tout sur la limite de 3 appareils, réinstallations OS, migrations
- **[Politique de remboursement](../legal/refund.fr.md)** — 14 jours, sans poser de questions

Besoin d'autre chose ? [Écrivez au support](mailto:neurocontrarian@gmail.com) — nous lisons chaque message.
