#!/usr/bin/env bash
# Smoke tests manuels pour l'API Réveil musical (nécessite jq et l'API démarrée).
set -eu

BASE="${BASE_URL:-http://127.0.0.1:8000}"
HDR=( -H "Content-Type: application/json" )
RUN_LIVE="${RUN_LIVE:-0}"

if ! command -v jq >/dev/null 2>&1; then
  echo "jq est requis (ex: brew install jq)" >&2
  exit 1
fi

post() {
  local query="$1"
  local body="$2"
  local tmp
  tmp=$(mktemp)

  echo ""
  echo ">>> POST $BASE/wakeup/trigger${query}"
  echo ">>> body: $body"
  http_code=$(curl -s -o "$tmp" -w "%{http_code}" -X POST \
    "$BASE/wakeup/trigger${query}" "${HDR[@]}" -d "$body")
  jq . < "$tmp"
  echo "HTTP $http_code"
  rm -f "$tmp"
}

echo "Base URL: $BASE"
echo "RUN_LIVE=$RUN_LIVE (1 = appels iTunes/MusicBrainz sans demo)"

echo ""
echo "========== 1. Démo — user-soleil, 4 météos (push) =========="
for W in SOLEIL PLUIE NEIGE NUAGEUX; do
  post "?demo=true" "{\"userId\":\"user-soleil\",\"dayOfWeek\":\"MONDAY\",\"weather\":\"$W\"}"
done

echo ""
echo "========== 2. Démo — canaux email / SMS =========="
post "?demo=true" '{"userId":"user-pluie","dayOfWeek":"TUESDAY","weather":"PLUIE"}'
post "?demo=true" '{"userId":"user-sms","dayOfWeek":"WEDNESDAY","weather":"SOLEIL"}'

echo ""
echo "========== 3. Démo — fallback morceau (user-pluie + SOLEIL) =========="
post "?demo=true" '{"userId":"user-pluie","dayOfWeek":"FRIDAY","weather":"SOLEIL"}'

echo ""
echo "========== 4. Erreurs =========="
post "?demo=true" '{"userId":"inconnu","dayOfWeek":"MONDAY","weather":"SOLEIL"}'
post "?demo=true" '{"userId":"user-soleil","dayOfWeek":"MONDAY","weather":"ORAGE"}'

if [ "$RUN_LIVE" = "1" ]; then
  echo ""
  echo "========== 5. APIs externes (sans demo) =========="
  post "" '{"userId":"user-soleil","dayOfWeek":"MONDAY","weather":"SOLEIL"}'
  echo "(2e appel — cache musique)"
  post "" '{"userId":"user-soleil","dayOfWeek":"MONDAY","weather":"SOLEIL"}'
  post "" '{"userId":"user-soleil","dayOfWeek":"SATURDAY","weather":"NEIGE"}'
  post "" '{"userId":"user-pluie","dayOfWeek":"MONDAY","weather":"PLUIE"}'
else
  echo ""
  echo "========== 5. APIs externes — ignoré =========="
  echo "Lancer avec RUN_LIVE=1 $0 pour tester iTunes/MusicBrainz."
fi

echo ""
echo "========== OpenAPI (extrait) =========="
curl -s "$BASE/openapi.json" | jq '.paths["/wakeup/trigger"]'

echo ""
echo "Terminé."
