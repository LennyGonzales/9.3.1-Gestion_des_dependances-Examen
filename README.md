# 9.3.1 — Examen Réveil musical

GONZALES Lenny

Service FastAPI qui déclenche un réveil musical : résolution du morceau (iTunes / MusicBrainz / secours local) et notification simulée sur le canal préféré de l'utilisateur (fourni par un service interne mocké).

## Architecture

Architecture **Ports & Adapters** (hexagonale) :

- `app/domain/` — modèles, ports, exceptions
- `app/services/` — `WakeupService` (orchestration)
- `app/infrastructure/` — adaptateurs musique, cache, profils utilisateurs, notifications
- `app/api/` — route HTTP et DTO
- `app/container.py` — injection de dépendances (`dependency-injector`)

Le **canal préféré** est lu depuis le mock du service interne (`UserProfilePort`), pas depuis l'appel HTTP.

## Prérequis

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

## Configuration

```bash
cp .env.example .env
```

| Variable | Description | Défaut |
|---|---|---|
| `MUSIC_PROVIDER` | `itunes` ou `musicbrainz` (fournisseur principal) | `itunes` |
| `ITUNES_URL` | Base URL iTunes Search | `https://itunes.apple.com` |
| `MUSICBRAINZ_URL` | Base URL MusicBrainz | `https://musicbrainz.org/ws/2` |
| `APP_USER_AGENT` | User-Agent (obligatoire pour MusicBrainz) | — |
| `HTTP_TIMEOUT` | Timeout HTTP (s) | `10.0` |
| `NOTIFICATION_FALLBACK_ORDER` | Ordre des canaux de secours | `push,email,sms` |

## Lancer l'API

```bash
docker compose up --build
```

Documentation : `http://127.0.0.1:8000/docs`

### Déclencher un réveil

```bash
curl -s -X POST "http://127.0.0.1:8000/wakeup/trigger?demo=true" \
  -H "Content-Type: application/json" \
  -d '{"userId":"user-soleil","dayOfWeek":"MONDAY","weather":"SOLEIL"}'
```

Utilisateurs de démo : `user-soleil` (push), `user-pluie` (email), `user-sms` (sms).

Mode `demo=true` : pas d'appel iTunes/MusicBrainz ; musique et notification simulées.

Sans `demo`, les APIs externes sont utilisées (avec cache pour limiter les appels iTunes).

## Tests

```bash
docker compose run --rm api pytest -v
```

Ou sans compose :

```bash
docker build -t reveil-musical .
docker run --rm reveil-musical pytest -v
```

## Licences des dépendances

Vérification automatique (liste blanche dans `licenses/allowlist.txt`) :

```bash
docker build -t reveil-musical .
docker run --rm -v "$(pwd):/repo:ro" reveil-musical sh /repo/scripts/check_licenses.sh /repo
```

Inventaire détaillé : voir `licenses/licenses.md` (généré via `pip-licenses` dans l'image Docker).

| Package | Version (image Docker) | Licence | Remarque |
|---|---|---|---|
| fastapi | voir `licenses/licenses.md` | MIT | OK |
| uvicorn | voir scan | BSD | OK |
| httpx | voir scan | BSD | OK |
| pydantic-settings | voir scan | MIT | OK |
| dependency-injector | voir scan | BSD | OK |
| pytest / pytest-asyncio / respx | voir scan | MIT / Apache-2.0 / BSD | OK (dev/test) |

Aucune dépendance copyleft forte ; `certifi` (copyleft faible) peut apparaître en MPL 2.0 (autorisé dans l'allowlist).

## Fiabilité

- **Musique** : provider principal → secondaire → catalogue local → piste minimale (jamais vide).
- **Notification** : canal préféré du profil → ordre de secours → canal d'urgence (log).
