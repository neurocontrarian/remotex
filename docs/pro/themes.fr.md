# Thèmes de boutons

!!! tip "Fonctionnalité Pro"
    Les thèmes de boutons nécessitent [Commandeck Pro](../pro.md). La version gratuite est limitée au thème **Gras**.

Les thèmes de boutons modifient le style visuel de toutes les tuiles dans la grille. Sélectionnez un thème depuis **Préférences → Apparence des boutons → Thème des boutons**.

---

## Thèmes disponibles

Il existe six thèmes. **Gras** et **Neon** conservent la couleur propre de chaque bouton ; **Cards**, **Phone keys**, **Retro** et **Tron** appliquent un style uniforme et ignorent les couleurs par bouton.

### Gras (par défaut)

Tuiles colorées pleines avec un fort contraste — la couleur de fond de chaque bouton en remplissage plat, texte blanc en gras. C'est le thème par défaut ; fonctionne bien en mode clair et sombre.

![Thème Gras](../assets/theme-bold.png)

### Cards

Tuiles claires en style « carte » avec une fine bordure teintée de l'accent. Sobre et neutre — un bon choix si les couleurs du thème Gras vous semblent trop fortes.

![Thème Cards](../assets/theme-cards.png)

### Phone keys

Touches compactes et arrondies avec une ombre douce, évoquant un clavier de téléphone ou de calculatrice. Fonctionne mieux avec une taille de bouton petite ou moyenne.

![Thème Phone keys](../assets/theme-phone.png)

### Neon

Vos couleurs de boutons avec un texte et des bordures cyan lumineux qui pulsent au survol. Idéal pour le mode sombre.

![Thème Neon](../assets/theme-neon.png)

!!! note
    La lueur de Neon est une animation au survol — elle s'apprécie mieux en utilisation. Survolez un bouton pour voir la bordure s'illuminer.

### Tron

Tuiles noires avec contours et texte cyan vif — un look « grille » façon Tron. Ignore les couleurs par bouton ; toutes les tuiles partagent le même style néon-sur-noir.

![Thème Tron](../assets/theme-tron.png)

### Retro

Monochrome ambre avec une bordure décalée nette, inspiré du terminal. Ignore les couleurs par bouton — toutes les tuiles se ressemblent intentionnellement.

![Thème Retro](../assets/theme-retro.png)

---

## CSS personnalisé

!!! tip "Fonctionnalité Pro"
    Le CSS personnalisé nécessite [Commandeck Pro](../pro.md).

Pour un contrôle visuel total, chargez votre propre feuille de style. Définissez le chemin dans **Préférences → Apparence des boutons → Fichier CSS personnalisé → Parcourir**. Commandeck utilise les **feuilles de style Qt (QSS)** — une syntaxe proche du CSS, mais avec les sélecteurs propres à Qt et un jeu de propriétés plus restreint que le CSS web.

Lorsqu'une feuille de style est chargée, elle est appliquée par-dessus le thème sélectionné. Vous pouvez combiner un thème de base avec de petits ajustements, ou écrire un thème complet depuis zéro.

### Cibles disponibles

Un bouton est un `QFrame` nommé `ButtonTile` contenant un `QLabel` nommé `TileLabel`. Ses
états (en cours, succès, échec, sélectionné) sont exposés comme **propriétés dynamiques**
que l'on cible avec des sélecteurs `[propriété="valeur"]` :

```css
/* Le conteneur de la tuile */
QFrame#ButtonTile {
  background: #1e1e2e;
  border-radius: 12px;
  border: 2px solid rgba(255, 255, 255, 0.15);
}

/* État de survol */
QFrame#ButtonTile:hover {
  border-color: rgba(137, 180, 250, 0.8);
}

/* État pressé */
QFrame#ButtonTile:pressed {
  background: #181825;
}

/* Le texte de l'étiquette */
QFrame#ButtonTile QLabel#TileLabel {
  color: #cdd6f4;
  font-weight: bold;
  font-size: 13px;
}

/* État en cours d'exécution (commande en cours) */
QFrame#ButtonTile[running="true"] {
  background: #313244;
}

/* Flash de succès */
QFrame#ButtonTile[success="true"] {
  border-color: #a6e3a1;
}

/* Flash d'échec */
QFrame#ButtonTile[error="true"] {
  border-color: #f38ba8;
}

/* Sélectionné (multi-sélection) */
QFrame#ButtonTile[selected="true"] {
  border-color: #89b4fa;
}
```

Cliquez sur **Exporter le modèle** dans les Préférences pour télécharger un fichier de départ contenant tous les sélecteurs disponibles avec leurs valeurs par défaut en commentaire.

!!! note
    Les feuilles de style Qt ne sont pas du CSS web : pas de `transform`, `box-shadow`,
    transition d'`opacity`, unité `rem`, ni `max-width`/`max-height`. Utilisez des couleurs
    pleines, des bordures et `border-radius` ; dimensionnez en pixels.
