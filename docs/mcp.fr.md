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

Remplacez `/chemin/vers/remotex` par votre chemin d'installation réel — généralement le dossier où vous avez cloné le dépôt.

---

## Ce que votre IA peut faire

| Outil | Description |
|-------|-------------|
| `list_buttons` | Lister tous les boutons, avec filtre optionnel par catégorie |
| `get_button` | Obtenir les détails d'un bouton par son nom ou son identifiant |
| `create_button` | Créer un nouveau bouton (nom, commande, catégorie, couleur, icône, apparence…) |
| `update_button` | Modifier n'importe quel champ d'un bouton existant — appelez d'abord `get_button` pour obtenir l'ID |
| `list_categories` | Lister tous les noms de catégories |
| `list_machines` | Lister les machines SSH (nom, hôte, utilisateur — sans clés privées) |

!!! note "La suppression n'est pas disponible via MCP"
    Les boutons ne peuvent être supprimés que depuis l'interface RemoteX (clic droit → Supprimer, ou multi-sélection). C'est intentionnel — cela empêche un assistant IA de supprimer accidentellement vos boutons.

!!! tip "Astuce pour modifier un bouton"
    Si l'IA dit qu'elle ne peut pas modifier un bouton, demandez-lui d'appeler d'abord `get_button` avec le nom du bouton pour récupérer l'ID, puis d'appeler `update_button` avec cet ID.

---

## Sécurité

Le serveur MCP utilise le **transport stdio** — il s'exécute en tant que sous-processus de votre client IA et communique uniquement via stdin/stdout. Aucun port réseau n'est ouvert. Seul le processus qui a lancé le serveur peut communiquer avec lui.

Lors de l'utilisation de mcpo (Open WebUI), le port HTTP (8000) est ouvert sur votre machine. Assurez-vous qu'il n'est pas exposé à des réseaux non fiables.

!!! warning
    Lorsque l'accès MCP est activé, votre assistant IA peut créer, modifier et supprimer des boutons. Désactivez cette option dans les Préférences lorsque vous n'en avez pas besoin.
