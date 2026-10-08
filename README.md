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

Le **morceau** est choisi uniquement à partir du couple **(jour, météo)** fourni à l'appel (grille dans le profil mock) ; si la paire est absente, morceau de secours `fallback_track_query`.

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

Tests manuels de l’API (avec `jq`, API démarrée via `docker compose up`) :

```bash
./scripts/smoke_test.sh
RUN_LIVE=1 ./scripts/smoke_test.sh   # inclut iTunes / MusicBrainz (sans demo)
BASE_URL=http://127.0.0.1:8000 ./scripts/smoke_test.sh
```

## Versions des dépendances (`requirements.txt`)

Les dépendances **directes** sont épinglées (`package==version`) pour :

1. **Reproductibilité** : même environnement en local, en CI et à la correction (`docker build` + `pytest` identiques).
2. **Audit des licences** : le sujet impose de documenter chaque composant avec sa version ; sans pin, un `pip install` ultérieur peut tirer une release plus récente et désaligner le README / `licenses/licenses.md`.
3. **Maîtrise des risques** : limiter les mises à jour transitives non voulies (rupture d’API, licence nouvelle ou non validée).

Les dépendances **transitives** (Starlette, Pydantic, ...) sont résolues à l’installation dans l’image Docker. L’inventaire complet est dans `licenses/licenses.md`. Pour monter de version : modifier `requirements.txt`, `docker build`, relancer les tests et `scripts/check_licenses.sh`, puis régénérer `licenses/licenses.md`.

## Licences des dépendances

Vérification automatique (liste blanche dans `licenses/allowlist.txt`) :

```bash
docker build -t reveil-musical .
docker run --rm -v "$(pwd):/repo:ro" reveil-musical sh /repo/scripts/check_licenses.sh /repo
```

Inventaire détaillé : voir `licenses/licenses.md` (généré via `pip-licenses` dans l'image Docker).


| Package | Version épinglée | Dernière stable (PyPI) | Écart | Licence | Justification |
|---|---|---|---|---|---|
| fastapi | 0.142.4 | 0.142.4 | — | MIT | Aligné sur la stable ; pin pour reproductibilité CI |
| uvicorn | 0.54.0 | 0.54.0 | — | BSD-3-Clause | Aligné sur la stable |
| httpx | 0.28.1 | 0.28.1 | — | BSD | Aligné sur la stable |
| pydantic-settings | 2.15.0 | 2.15.0 | — | MIT | Aligné sur la stable |
| dependency-injector | 4.49.1 | 4.49.1 | — | BSD | Aligné sur la stable |
| pytest | 9.1.1 | 9.1.1 | — | MIT | dev/test ; aligné sur la stable |
| pytest-asyncio | 1.4.0 | 1.4.0 | — | Apache-2.0 | dev/test ; aligné sur la stable |
| respx | 0.23.1 | 0.23.1 | — | BSD | dev/test ; aligné sur la stable |

Aucune dépendance copyleft forte ; `certifi` (copyleft faible) peut apparaître en MPL 2.0 (autorisé dans l'allowlist).

## Fiabilité

- **Musique** : provider principal → secondaire → catalogue local → piste minimale (jamais vide). iTunes renvoie `429` → bascule vers le fournisseur secondaire / secours ; le cache limite les appels répétés (~20 req/min côté iTunes).
- **Notification** : canal préféré du profil → ordre de secours → canal d'urgence (log structuré, sans état partagé entre requêtes).
