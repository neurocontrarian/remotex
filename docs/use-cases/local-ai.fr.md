# Cas d'usage : Piloter Commandeck depuis une IA locale

!!! tip "Fonctionnalité Pro"
    L'intégration IA (MCP) nécessite [Commandeck Pro](../pro.fr.md).

🔰 **L'idée :** au lieu de construire les boutons à la main, vous *demandez* à un assistant IA — « ajoute un bouton qui redémarre Nginx dans la catégorie Serveur » — et il le crée pour vous. L'IA peut lire vos boutons, machines et profils, et (si vous l'autorisez) les exécuter. Ça marche avec des assistants cloud comme Claude **et** avec un modèle entièrement local tournant sur votre propre matériel.

Cette page parcourt le chemin du modèle local de bout en bout avec **Open WebUI** + un LLM local (par ex. Llama, Gemma). Pour la liste complète des clients et options, voir la [référence Intégration IA](../pro/mcp.fr.md).

## Pourquoi local ?

Un modèle local garde tout sur votre machine — vos boutons, commandes et noms de serveurs ne quittent jamais votre réseau. Parfait pour un homelab et les configurations soucieuses de confidentialité.

## Pas à pas

### 1. Activer l'accès MCP

**Préférences → Intégration bureau → Autoriser l'accès MCP.**

![Autoriser l'accès MCP](../assets/preferences-desktop.png)

### 2. Lancer le serveur MCP de Commandeck

Le serveur est intégré à l'application. Lancez votre build Commandeck avec `--mcp-server` :

```bash
/chemin/vers/Commandeck-Pro-VERSION-Linux-x86_64.AppImage --mcp-server
```

!!! warning "Lancez-le sous l'utilisateur qui utilise Commandeck"
    Le serveur lit les boutons de **celui qui le lance**. Lancez-le depuis un terminal connecté en tant que votre utilisateur de bureau habituel, sinon l'IA verra le mauvais jeu de boutons (ou un jeu vide).

### 3. Faire le pont vers Open WebUI avec mcpo

Open WebUI dialogue avec les outils via HTTP : placez le proxy [mcpo](https://github.com/open-webui/mcpo) devant :

```bash
mcpo --port 8000 -- /chemin/vers/Commandeck-Pro-VERSION-Linux-x86_64.AppImage --mcp-server
```

Puis dans Open WebUI : **Admin Panel → Settings → Tools → +**, type **OpenAPI**, URL `http://<ip-de-la-machine>:8000`. Si Open WebUI tourne sur une autre machine, utilisez l'IP de la machine qui fait tourner mcpo — pas `localhost`.

### 4. Dialoguer avec vos boutons

Démarrez un chat, activez l'outil **commandeck**, collez le [prompt système recommandé](../pro/mcp.fr.md#prompt-systeme-recommande), et essayez :

> *« Liste mes boutons. »*
> *« Ajoute un bouton appelé "Espace disque" qui exécute `df -h` dans la catégorie Système. »*

Appuyez sur **F5** dans Commandeck pour voir les nouveaux boutons apparaître.

⚙️ **Notes pour les utilisateurs avancés**

- **Le modèle compte.** La couche outils est indépendante du modèle, mais la qualité du tool-calling varie beaucoup. Les modèles instruction-tuned fonctionnent le mieux ; les petits modèles locaux ont souvent besoin du prompt système pour appeler les outils de façon fiable.
- **Laisser l'IA *exécuter* des boutons** est une autorisation séparée à trois verrous (interrupteur global + drapeau par bouton + confirmation optionnelle). Désactivé par défaut. Voir [Autoriser l'IA à exécuter](../pro/mcp.fr.md#autoriser-lia-a-executer-des-boutons).
- **Rendre le pont persistant :** un service systemd utilisateur garde mcpo actif au redémarrage — voir la [référence MCP](../pro/mcp.fr.md).
