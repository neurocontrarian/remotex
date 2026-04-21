# Intégration IA (MCP)

!!! warning "Expérimental"
    L'intégration IA est expérimentale. La prise en charge des outils et leur comportement varient selon les modèles et les clients. Les résultats ne sont pas garantis — vérifiez toujours ce que l'IA crée ou modifie.

RemoteX inclut un serveur MCP (Model Context Protocol). Une fois configuré, votre assistant IA peut lire et gérer vos boutons directement — sans copier-coller ni expliquer votre configuration.

> *"Ajoute un bouton appelé 'Redémarrer Nginx' qui exécute `sudo systemctl restart nginx` dans la catégorie Serveur"*

## Étape 1 — Activer l'accès MCP dans RemoteX

MCP est **désactivé par défaut**. Activez-le une seule fois :

**Préférences → Intégration bureau → Autoriser l'accès MCP**

## Étape 2 — Configurer votre client IA

Choisissez votre outil ci-dessous. La configuration est effectuée une seule fois ; ensuite, tout fonctionne automatiquement.

=== "Claude Desktop"

    **Emplacement du fichier de configuration :**

    | Système | Chemin |
    |---------|--------|
    | Linux | `~/.config/Claude/claude_desktop_config.json` |
    | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
    | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

    Ajoutez ceci dans le fichier (créez-le s'il n'existe pas) :

    ```json
    {
      "mcpServers": {
        "remotex": {
          "command": "python3",
          "args": ["/chemin/vers/remotex/src/mcp_server.py"]
        }
      }
    }
    ```

    Redémarrez Claude Desktop. RemoteX apparaîtra comme un outil connecté.

=== "Claude Code"

    Exécutez cette commande une fois dans un terminal :

    ```bash
    claude mcp add remotex python3 /chemin/vers/remotex/src/mcp_server.py
    ```

    Pour vérifier : `claude mcp list`

=== "Cursor"

    Modifiez `~/.cursor/mcp_config.json` :

    ```json
    {
      "mcpServers": {
        "remotex": {
          "command": "python3",
          "args": ["/chemin/vers/remotex/src/mcp_server.py"]
        }
      }
    }
    ```

    Redémarrez Cursor.

=== "Windsurf"

    Modifiez `~/.codeium/windsurf/mcp_config.json` :

    ```json
    {
      "mcpServers": {
        "remotex": {
          "command": "python3",
          "args": ["/chemin/vers/remotex/src/mcp_server.py"]
        }
      }
    }
    ```

    Redémarrez Windsurf.

=== "Continue.dev"

    Ajoutez dans `.continue/config.yaml` dans votre projet :

    ```yaml
    mcpServers:
      - name: remotex
        command: python3
        args:
          - /chemin/vers/remotex/src/mcp_server.py
    ```

    Les outils MCP ne sont disponibles qu'en **mode Agent**.

=== "Open WebUI (llama.cpp / Ollama)"

    Open WebUI se connecte aux outils via HTTP, pas stdio. Utilisez [mcpo](https://github.com/open-webui/mcpo) (le proxy officiel Open WebUI) pour faire le pont avec RemoteX.

    **Étape 1 — Installer mcpo (une seule fois) :**

    ```bash
    pip install mcpo
    # si pip est bloqué par votre OS (externally-managed-environment) :
    pipx install mcpo
    ```

    **Étape 2 — Trouver l'IP locale de votre machine (si Open WebUI est sur une autre machine) :**

    ```bash
    hostname -I | awk '{print $1}'
    ```

    Notez cette IP — vous en aurez besoin à l'étape 4.

    **Étape 3 — Lancer le proxy (garder ce terminal ouvert) :**

    ```bash
    mcpo --port 8000 -- python3 /chemin/vers/remotex/src/mcp_server.py
    ```

    Vous devriez voir : `Uvicorn running on http://0.0.0.0:8000`

    **Étape 4 — Ajouter le serveur d'outils dans Open WebUI :**

    Allez dans **Admin Panel → Integrations → Manage tool servers → `+`** et remplissez :

    | Champ | Valeur |
    |-------|--------|
    | Type | **OpenAPI** |
    | Name | `remotex` |
    | URL | `http://<votre-ip>:8000` |
    | Auth | None |

    !!! warning "Utilisez l'IP de votre machine, pas localhost"
        Si Open WebUI tourne sur une autre machine (ex : un serveur), `localhost` pointerait vers ce serveur — pas vers votre machine Linux Mint où mcpo tourne. Utilisez l'IP obtenue à l'étape 2.

    **Étape 5 — Activer l'outil dans un chat :**

    Démarrez un nouveau chat, cliquez sur l'icône **`+`** (outils) près du champ de saisie, et activez **remotex**.

    !!! tip
        Cela fonctionne avec n'importe quel backend supporté par Open WebUI — llama.cpp, Ollama, API compatibles OpenAI, etc. La couche outils est indépendante du modèle. La prise en charge du tool-calling varie selon le modèle — les modèles instruction-tuned fonctionnent généralement mieux.

    ---

    **Quand redémarrer mcpo**

    mcpo lance `mcp_server.py` comme sous-processus au démarrage et le garde en mémoire. Vous devez redémarrer mcpo chaque fois que :

    - Vous mettez à jour RemoteX (`git pull`) — l'ancien `mcp_server.py` reste chargé jusqu'au redémarrage
    - Vous activez ou désactivez **Autoriser l'accès MCP** dans les Préférences

    Si vous utilisez systemd (voir ci-dessous) : `systemctl --user restart mcpo-remotex`

    Sinon : appuyez sur `Ctrl+C` dans le terminal mcpo et relancez l'étape 3.

    ---

    **Étape 6 — (Optionnel) Rendre mcpo persistant au redémarrage**

    Créez un service systemd utilisateur pour que mcpo démarre automatiquement à la connexion :

    ```bash
    mkdir -p ~/.config/systemd/user
    cat > ~/.config/systemd/user/mcpo-remotex.service << 'EOF'
    [Unit]
    Description=mcpo proxy pour le serveur MCP RemoteX

    [Service]
    ExecStart=%h/.local/bin/mcpo --port 8000 -- %h/remotex/.venv/bin/python3 %h/remotex/src/mcp_server.py
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=default.target
    EOF

    systemctl --user daemon-reload
    systemctl --user enable --now mcpo-remotex
    ```

    Commandes utiles :

    ```bash
    systemctl --user status mcpo-remotex    # vérifier l'état
    systemctl --user restart mcpo-remotex   # redémarrer après un git pull
    systemctl --user stop mcpo-remotex      # arrêter
    journalctl --user -u mcpo-remotex -f    # logs en direct
    ```

    !!! note
        Ajustez les chemins dans `ExecStart` si votre installation RemoteX n'est pas dans `~/remotex` ou si mcpo n'est pas installé via pipx. Lancez `which mcpo` pour trouver le bon chemin.

Remplacez `/chemin/vers/remotex` par votre chemin d'installation réel — généralement le dossier où vous avez cloné le dépôt.

---

## Prompt système recommandé

Collez le prompt ci-dessous dans le champ de prompt système de votre client IA. Il couvre deux choses :
prépare le modèle à utiliser le tool `help` en cas de doute, **et** lui apprend à décomposer
les commandes shell complexes en composants RemoteX plutôt que de les coller telles quelles.

```
You are a RemoteX assistant. RemoteX is a Linux desktop app that runs local and SSH shell commands via a button grid.

Key concepts:
- Buttons have: command, category, icon, color, execution_mode (silent / output / terminal).
- Execution Profiles (Pro): named context with run_as_user, working_dir, and an optional sudo
  password stored in the system keyring. One profile can be shared across many buttons.
- Machines (Pro): SSH targets a button can run on.

When a user asks you to add or refactor a shell command, decompose it before creating a button:
1. `cd /some/path` → Execution Profile working_dir (strip from command)
2. `sudo -u user` wrapper → Execution Profile run_as_user (strip the wrapper, keep the inner command)
3. Opens an interactive shell (bash, zsh, exec bash) → execution_mode = "terminal"
4. Produces output the user wants to read → execution_mode = "output"; fire-and-forget → "silent"
5. What remains after stripping context wrappers is the command field.

Example: `sudo -u claude-ai bash -c 'cd /home/projects && exec bash'`
→ Guide the user to create a Profile: run_as_user=claude-ai, working_dir=/home/projects
→ Create button: command=bash, execution_mode=terminal, assign that profile

Important: Execution Profiles cannot be created via MCP — guide the user to create one first
in the RemoteX UI (Menu → Manage Profiles), then create the button.

If unsure which tool to call, call the `help` tool first.
```

=== "Open WebUI"

    Dans Open WebUI, allez dans **Admin Panel → Settings → System prompt** et collez le prompt
    ci-dessus (ou dans le champ de prompt système des paramètres du modèle dans le chat).

=== "Claude Desktop"

    Claude Desktop n'expose pas de champ de prompt système. La description du tool `help` est
    suffisamment explicite pour Claude — aucun prompt supplémentaire n'est nécessaire.

=== "Autres clients"

    Collez le prompt dans le champ de prompt système ou d'instructions que votre client expose
    avant le début de la conversation.

---

## Ce que votre IA peut faire

| Outil | Description |
|-------|-------------|
| `help` | Retourner le guide complet des workflows — à appeler en premier si vous ne savez pas comment procéder |
| `list_buttons` | Lister tous les boutons, avec filtre optionnel par catégorie |
| `get_button` | Obtenir les détails d'un bouton par son nom ou son identifiant |
| `create_button` | Créer un nouveau bouton (nom, commande, catégorie, couleur, icône, apparence…) |
| `update_button` | Modifier n'importe quel champ d'un bouton existant — appelez d'abord `get_button` pour obtenir l'ID |
| `list_categories` | Lister tous les noms de catégories |
| `list_machines` | Lister les machines SSH (nom, hôte, utilisateur — sans clés privées) |

!!! note "La suppression n'est pas disponible via MCP"
    Les boutons ne peuvent être supprimés que depuis l'interface RemoteX (clic droit → Supprimer, ou multi-sélection). C'est intentionnel — cela empêche un assistant IA de supprimer accidentellement vos boutons.

!!! tip "Rafraîchir la grille après des modifications par l'IA"
    Après qu'une IA a créé ou modifié un bouton, appuyez sur **F5** (ou menu → Refresh Buttons) pour recharger la grille sans redémarrer RemoteX.

!!! tip "Astuce pour modifier un bouton"
    Si l'IA dit qu'elle ne peut pas modifier un bouton, demandez-lui d'appeler d'abord `get_button` avec le nom du bouton pour récupérer l'ID, puis d'appeler `update_button` avec cet ID.

---

## Sécurité

Le serveur MCP utilise le **transport stdio** — il s'exécute en tant que sous-processus de votre client IA et communique uniquement via stdin/stdout. Aucun port réseau n'est ouvert. Seul le processus qui a lancé le serveur peut communiquer avec lui.

Lors de l'utilisation de mcpo (Open WebUI), le port HTTP (8000) est ouvert sur votre machine. Assurez-vous qu'il n'est pas exposé à des réseaux non fiables.

!!! warning
    Lorsque l'accès MCP est activé, votre assistant IA peut créer, modifier et supprimer des boutons. Désactivez cette option dans les Préférences lorsque vous n'en avez pas besoin.
