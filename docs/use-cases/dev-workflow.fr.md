# Cas d'utilisation : Workflow de développement

Ce guide montre comment utiliser RemoteX comme palette de commandes pour développeur. L'objectif : remplacer les commandes de terminal les plus répétitives par des boutons en un clic, organisés par projet.

## Le scénario

Vous travaillez sur deux projets :

- Un **frontend** (application React, en exécution locale)
- Une API **backend** (Node.js, déployée sur un VPS distant)

Vous exécutez les mêmes commandes des dizaines de fois par jour : build, test, déploiement, consultation des logs. RemoteX remplace vos réflexes musculaires par des boutons visibles et étiquetés.

---

## Étape 1 — Ajouter votre serveur comme machine SSH

Pour les commandes qui s'exécutent sur le VPS, commencez par l'ajouter :

| Champ | Valeur |
|-------|--------|
| Nom | `VPS Production` |
| Hôte | `ip-de-votre-vps` |
| Utilisateur SSH | `deploy` |
| Chemin de la clé SSH | `~/.ssh/id_ed25519` |

Cliquez sur **Tester** pour vérifier la connectivité.

!!! tip "Fonctionnalité Pro"
    Les machines SSH nécessitent [RemoteX Pro](../pro.md).

---

## Étape 2 — Catégorie Frontend

Créez ces boutons avec **Catégorie : Frontend**.

### Installer les dépendances

```
npm install
```

- Mode d'exécution : **Afficher la sortie** (voir si quelque chose échoue)
- Conseil répertoire de travail : préfixez avec `cd ~/projects/myapp &&`

Commande complète : `cd ~/projects/myapp && npm install`

---

### Démarrer le serveur de développement

```
cd ~/projects/myapp && npm run dev
```

- Mode d'exécution : **Ouvrir dans le terminal** — le serveur de développement est interactif et diffuse la sortie en continu

---

### Build pour la production

```
cd ~/projects/myapp && npm run build
```

- Mode d'exécution : **Afficher la sortie** — vous voulez voir les erreurs de build
- Icône : `package-x-generic-symbolic`

---

### Exécuter les tests

```
cd ~/projects/myapp && npm test -- --watchAll=false
```

- Mode d'exécution : **Afficher la sortie**
- Infobulle : `Exécuter la suite de tests Jest complète une seule fois`

---

### Lint

```
cd ~/projects/myapp && npm run lint
```

- Mode d'exécution : **Afficher la sortie**
- Couleur : `#1c71d8` (bleu — informatif)

---

## Étape 3 — Catégorie Backend

Créez ces boutons avec **Catégorie : Backend**. Cible : `VPS Production`.

### Récupérer le dernier code

```
cd ~/app && git pull origin main
```

- Mode d'exécution : **Afficher la sortie**
- Confirmer avant d'exécuter : activé (évite les déploiements accidentels)

---

### Redémarrer le serveur API

```
sudo systemctl restart myapp
```

- Mode d'exécution : **Silencieux**
- Confirmer avant d'exécuter : activé

---

### Docker : rebuild et redémarrage

```
cd ~/app && docker compose down && docker compose up -d --build
```

- Mode d'exécution : **Afficher la sortie**
- Infobulle : `Reconstruire les conteneurs et redémarrer (~30s)`
- Couleur : `#26a269` (vert — action de déploiement)

---

### Suivre les logs de l'application

```
sudo journalctl -u myapp -f -n 100
```

- Mode d'exécution : **Ouvrir dans le terminal** — `journalctl -f` diffuse indéfiniment

---

### Vérifier les conteneurs Docker

```
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

- Mode d'exécution : **Afficher la sortie**

---

### Sauvegarde de la base de données

```
cd ~/app && pg_dump mydb > ~/backups/mydb_$(date +%Y%m%d).sql
```

- Mode d'exécution : **Afficher la sortie**
- Confirmer avant d'exécuter : activé
- Infobulle : `Exporter la base de données de production dans ~/backups/`

---

## Étape 4 — Utiliser "Afficher la sortie" de façon stratégique

Toutes les commandes n'ont pas besoin de **Afficher la sortie**. Une bonne règle :

| Utilisez **Silencieux** pour | Utilisez **Afficher la sortie** pour | Utilisez **Ouvrir dans le terminal** pour |
|------------------------------|--------------------------------------|-------------------------------------------|
| Redémarrages de services | Builds et tests | Processus interactifs (`htop`, `vim`, `psql`) |
| Déclencheurs simples | Commandes pouvant échouer | Flux de longue durée (`tail -f`, `docker logs -f`) |
| Déploiements de confiance | Tout ce qui a un stdout significatif | Sessions SSH |

---

## Étape 5 — Migration vers un nouveau serveur

Lorsque votre VPS est mis à niveau ou migré, vous n'avez pas besoin de modifier chaque bouton individuellement. Utilisez la [sélection multiple](../pro/multiselect.md) pour réassigner tous les boutons Backend en une seule opération :

1. Activez le mode de sélection (☑ dans la barre d'en-tête)
2. Cliquez sur chaque bouton Backend, ou faites un rubber-band pour tous les sélectionner
3. Cliquez sur **Machine** dans la barre d'actions en bas
4. Choisissez le nouveau serveur

Tous les boutons sélectionnés sont mis à jour en une seule opération.

---

## Résultat

Deux onglets de catégorie propres — Frontend et Backend — font apparaître exactement les commandes dont vous avez besoin. Votre terminal reste ouvert pour le travail exploratoire ; RemoteX gère les parties répétitives.

!!! tip
    Maintenez le nombre de boutons par catégorie autour de 6–10. Au-delà, la navigation devient aussi complexe qu'avec le terminal.
