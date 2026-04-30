# Use Case: Development Workflow

This guide shows how to use RemoteX as a developer's command palette. The goal: replace the most repetitive terminal commands with one-click buttons, organised by project.

## The scenario

You work on two projects:

- A **frontend** (React app, running locally)
- A **backend** API (Node.js, deployed on a remote VPS)

You run the same commands dozens of times a day: build, test, deploy, check logs. RemoteX replaces your muscle memory with visible, labelled buttons.

---

## Step 1 — Add your server as an SSH machine

For commands that run on the VPS, add it first:

| Field | Value |
|-------|-------|
| Name | `VPS Production` |
| Host | `your-vps-ip` |
| SSH User | `deploy` |
| SSH Key Path | `~/.ssh/id_ed25519` |

Click **Test** to verify connectivity.

!!! tip "Pro feature"
    SSH machines require [RemoteX Pro](../pro.md).

---

## Step 2 — Frontend category

Create these buttons with **Category: Frontend**.

### Install dependencies

```
npm install
```

- Execution mode: **Show output** (see if something fails)
- Working directory tip: prefix with `cd ~/projects/myapp &&`

Full command: `cd ~/projects/myapp && npm install`

---

### Start dev server

```
cd ~/projects/myapp && npm run dev
```

- Execution mode: **Open in terminal** — the dev server is interactive and streams output continuously

---

### Build for production

```
cd ~/projects/myapp && npm run build
```

- Execution mode: **Show output** — you want to see build errors
- Icon: `package-x-generic-symbolic`

---

### Run tests

```
cd ~/projects/myapp && npm test -- --watchAll=false
```

- Execution mode: **Show output**
- Tooltip: `Run the full Jest test suite once`

---

### Lint

```
cd ~/projects/myapp && npm run lint
```

- Execution mode: **Show output**
- Color: `#1c71d8` (blue — informational)

---

## Step 3 — Backend category

Create these buttons with **Category: Backend**. Target: `VPS Production`.

### Pull latest code

```
cd ~/app && git pull origin main
```

- Execution mode: **Show output**
- Confirm before running: enabled (avoids accidental deploys)

---

### Restart API server

```
sudo systemctl restart myapp
```

- Execution mode: **Silent**
- Confirm before running: enabled

---

### Docker: rebuild and restart

```
cd ~/app && docker compose down && docker compose up -d --build
```

- Execution mode: **Show output**
- Tooltip: `Rebuild containers and restart (takes ~30s)`
- Color: `#26a269` (green — deploy action)

---

### Tail application logs

```
sudo journalctl -u myapp -f -n 100
```

- Execution mode: **Open in terminal** — `journalctl -f` streams indefinitely

---

### Check Docker containers

```
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

- Execution mode: **Show output**

---

### Database backup

```
cd ~/app && pg_dump mydb > ~/backups/mydb_$(date +%Y%m%d).sql
```

- Execution mode: **Show output**
- Confirm before running: enabled
- Tooltip: `Dump the production database to ~/backups/`

---

## Step 4 — Use "Show output" strategically

Not every command needs **Show output**. A good rule:

| Use **Silent** for | Use **Show output** for | Use **Open in terminal** for |
|--------------------|------------------------|------------------------------|
| Service restarts | Builds and tests | Interactive processes (`htop`, `vim`, `psql`) |
| Simple triggers | Commands that can fail | Long-running streams (`tail -f`, `docker logs -f`) |
| Deploys you trust | Anything with meaningful stdout | SSH sessions |

---

## Step 5 — Migrating to a new server

When your VPS is upgraded or migrated, you don't need to edit each button individually. Use [multi-select](../pro/multiselect.md) to reassign all Backend buttons at once:

1. Enter select mode (☑ in the header bar)
2. Click each Backend button, or rubber-band select them all
3. Click **Machine** in the action bar at the bottom
4. Choose the new server

All selected buttons are updated in one operation.

---

## Result

Two clean category tabs — Frontend and Backend — surface exactly the commands you need. Your terminal stays open for exploratory work; RemoteX handles the repetitive parts.

!!! tip
    Keep the number of buttons per category to around 6–10. More than that and it becomes as hard to navigate as the terminal.
