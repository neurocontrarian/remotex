# Fenêtre principale

![Fenêtre principale de RemoteX](../assets/main-window.png)

La fenêtre principale est divisée en quatre zones : la **barre d'en-tête**, la **barre de catégories**, la **barre de recherche** et la **grille de boutons**.

---

## Barre d'en-tête

La barre d'en-tête est toujours visible. De gauche à droite :

### + (Ajouter un bouton)

Ouvre l'[Éditeur de bouton](button-editor.md) pour créer un nouveau bouton. Raccourci clavier : `Ctrl+N`.

!!! note
    La version gratuite autorise jusqu'à 3 boutons personnalisés. Le bouton **+** est grisé une fois la limite atteinte. [RemoteX Pro](../pro.md) supprime cette limite.

### Icône de recherche

Affiche ou masque la barre de recherche. Vous pouvez également commencer à taper n'importe où dans la fenêtre pour l'ouvrir automatiquement.

### Icône de sélection (☑)

Active le mode de sélection multiple. Dans ce mode, cliquer sur un bouton bascule sa sélection au lieu de l'exécuter. Une barre d'actions apparaît en bas pour les opérations groupées.

!!! tip "Fonctionnalité Pro"
    La sélection multiple nécessite [RemoteX Pro](../pro.md).

### Menu hamburger (≡)

Ouvre le menu de l'application :

- **Gérer les machines** — ouvre la liste des machines (Pro uniquement)
- **Toujours au premier plan** — bascule si la fenêtre flotte au-dessus de toutes les autres fenêtres (option à bascule avec état, cochée lorsqu'active)
- **Préférences** — ouvre la boîte de dialogue des préférences (`Ctrl+,`)
- **Raccourcis clavier** — affiche tous les raccourcis (`Ctrl+?`)
- **À propos de RemoteX** — informations sur la version et la licence

---

## Barre de catégories

La barre de catégories apparaît sous l'en-tête dès qu'au moins un bouton possède une catégorie. Elle est masquée lorsque tous les boutons sont sans catégorie.

### Pastille Tout

La pastille la plus à gauche. La sélectionner affiche la grille complète, indépendamment des catégories. Elle est sélectionnée par défaut.

### Pastilles de catégories

Une pastille par catégorie, dans l'ordre d'apparition des catégories dans la grille. Cliquer sur une pastille filtre la grille sur cette catégorie uniquement. Une seule pastille peut être active à la fois (comportement radio).

### Clic droit sur une pastille

Un clic droit sur une pastille de catégorie ouvre un petit menu :

- **Masquer la catégorie** — retire la pastille et masque tous les boutons de cette catégorie dans la grille. Les boutons ne sont pas supprimés.

Pour afficher à nouveau une catégorie masquée, allez dans **Préférences → Catégories** et réactivez-la.

---

## Barre de recherche

La barre de recherche apparaît sous la barre de catégories lorsqu'elle est activée. Elle filtre les boutons en temps réel par leur nom d'étiquette. Le filtre s'applique en complément de tout filtre de catégorie actif.

Appuyez sur `Échap` ou cliquez à nouveau sur l'icône de recherche pour fermer la barre de recherche et effacer le filtre.

---

## Grille de boutons

La zone de contenu principale est une grille défilable de [tuiles de boutons](#tuiles-de-boutons). Le nombre de colonnes est défini dans **Préférences → Mise en page → Boutons par ligne** et s'applique en direct sans redémarrage.

Glissez-déposez n'importe quel bouton pour le réorganiser dans la grille.

### Tuiles de boutons

Chaque tuile affiche :

- Une **icône** (en haut ou au centre, selon la taille)
- Une **étiquette** (le nom du bouton)

La couleur de fond de la tuile et la couleur de l'étiquette peuvent être personnalisées par bouton.

**Clic gauche** sur une tuile pour exécuter la commande. Si le bouton a **Confirmer avant d'exécuter** activé, une boîte de dialogue demande une confirmation préalable. Si le bouton cible plusieurs machines, un [sélecteur de machine](ssh-machines.md#le-sélecteur-de-machine) s'affiche.

**Clic droit** sur une tuile pour ouvrir le menu contextuel :

- **Modifier** — ouvre l'éditeur de bouton pour ce bouton
- **Dupliquer** — crée une copie du bouton
- **Déplacer vers la catégorie** — saisissez ou choisissez un nom de catégorie pour réassigner
- **Supprimer** — supprime définitivement le bouton (confirmation requise)

!!! note
    Les boutons par défaut (Linux Essentials, Développement) ne peuvent pas être modifiés dans la version gratuite. Le clic droit affiche l'option **Modifier** avec une icône de verrou. [RemoteX Pro](../pro.md) déverrouille la modification.

---

## Notifications toast

Après l'exécution d'une commande, une petite notification toast remonte depuis le bas de la fenêtre :

- **Toast vert** — la commande a réussi
- **Toast rouge** — la commande a échoué (code de sortie non nul)

Pour les commandes en mode **Afficher la sortie**, ou pour toute commande qui échoue, une boîte de dialogue s'ouvre automatiquement avec le `stdout` et le `stderr` complets.

---

## État vide

Si aucun bouton ne correspond à la recherche ou au filtre de catégorie actuel, une illustration d'état vide s'affiche avec un conseil. Ce n'est pas une erreur — cela signifie simplement que tous les boutons sont filtrés. Cliquez sur **Tout** ou effacez la recherche pour voir à nouveau vos boutons.

Si vous n'avez aucun bouton (inhabituel après une nouvelle installation), l'état vide affiche une invite pour ajouter votre premier bouton.
