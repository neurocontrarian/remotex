# Intégration IA (MCP)

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

=== "Open WebUI"

    !!! note
        Open WebUI ne prend en charge que les serveurs MCP **basés sur HTTP**, pas le transport stdio utilisé par RemoteX. La connexion directe n'est pas supportée.

        En guise de solution de contournement, vous pouvez utiliser [mcpo](https://github.com/open-webui/mcpo) pour exposer le serveur MCP de RemoteX via HTTP, mais il s'agit d'une configuration avancée.

Remplacez `/chemin/vers/remotex` par votre chemin d'installation réel — généralement le dossier où vous avez cloné le dépôt.

---

## Ce que votre IA peut faire

| Outil | Description |
|-------|-------------|
| `list_buttons` | Lister tous les boutons, avec filtre optionnel par catégorie |
| `get_button` | Obtenir les détails d'un bouton par son nom ou son identifiant |
| `create_button` | Créer un nouveau bouton |
| `update_button` | Modifier les champs d'un bouton existant |
| `delete_button` | Supprimer un bouton |
| `list_categories` | Lister tous les noms de catégories |
| `list_machines` | Lister les machines SSH (nom, hôte, utilisateur — sans clés privées) |

---

## Sécurité

Le serveur MCP utilise le **transport stdio** — il s'exécute en tant que sous-processus de votre client IA et communique uniquement via stdin/stdout. Aucun port réseau n'est ouvert. Seul le processus qui a lancé le serveur peut communiquer avec lui.

!!! warning
    Lorsque l'accès MCP est activé, votre assistant IA peut créer, modifier et supprimer des boutons. Désactivez cette option dans les Préférences lorsque vous n'en avez pas besoin.
