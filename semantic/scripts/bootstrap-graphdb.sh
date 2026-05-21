#!/bin/sh
# ============================================================
#  bootstrap-graphdb.sh
#  Creates a GeoSPARQL-enabled GraphDB repository and loads
#  all ontologies into named graphs.
# ============================================================

set -e

GRAPHDB_URL="${GRAPHDB_URL:-http://localhost:7200}"
REPO="${REPO:-citygml}"
ONT_DIR="/ontologies"

echo "=================================================="
echo "  Setting up GraphDB repo: $REPO"
echo "=================================================="

# ── Create repository with GeoSPARQL enabled ──────────────
echo "[REPO]  Creating repository $REPO"
curl -sf -X POST "${GRAPHDB_URL}/rest/repositories" \
  -H "Content-Type: application/json" \
  -d "{
    \"id\": \"${REPO}\",
    \"type\": \"free\",
    \"title\": \"CityGML + GeoSPARQL\",
    \"params\": {
      \"defaultNS\": { \"name\": \"defaultNS\", \"value\": \"\" },
      \"enablePredicateList\": { \"name\": \"enablePredicateList\", \"value\": \"true\" },
      \"enableRDFRank\": { \"name\": \"enableRDFRank\", \"value\": \"false\" },
      \"inMemoryLiteralProperties\": { \"name\": \"inMemoryLiteralProperties\", \"value\": \"true\" },
      \"enableFtsIndex\": { \"name\": \"enableFtsIndex\", \"value\": \"false\" },
      \"enableGeoSparqlPlugin\": { \"name\": \"enableGeoSparqlPlugin\", \"value\": \"true\" },
      \"geoSparqlPlugin.maxResultCache\": { \"name\": \"geoSparqlPlugin.maxResultCache\", \"value\": \"500\" }
    }
  }" && echo "[OK]    Repository created" || echo "[INFO]  Repository may already exist"

# ── Helper: download if not cached ─────────────────────────
fetch() {
  local name="$1" url="$2" file="${ONT_DIR}/$name"
  [ -f "$file" ] && echo "[SKIP]  $name cached" && return
  echo "[DL]    $name"
  curl -sL --retry 3 -o "$file" "$url" && echo "[OK]    $name" || echo "[WARN]  Failed: $name"
}

# ── Helper: load into named graph via GraphDB REST ─────────
upload() {
  local name="$1" graph="$2" file="${ONT_DIR}/$name"
  [ -f "$file" ] || { echo "[SKIP]  $name missing"; return; }
  echo "[LOAD]  $name → <$graph>"
  curl -sf -X POST \
    "${GRAPHDB_URL}/repositories/${REPO}/rdf-graphs/service?graph=${graph}" \
    -H "Content-Type: text/turtle" \
    --data-binary "@${file}" \
    && echo "[OK]    Loaded" || echo "[WARN]  Load failed"
}

# ── Download + load all ontologies ─────────────────────────

fetch "bot.ttl"             "https://raw.githubusercontent.com/w3c-lbd-cg/bot/master/bot.ttl"
fetch "sosa.ttl"            "https://www.w3.org/ns/sosa/"
fetch "ssn.ttl"             "https://www.w3.org/ns/ssn/"
fetch "geosparql11.ttl"     "https://opengeospatial.github.io/ogc-geosparql/geosparql11/geo.ttl"
fetch "citygml-core.ttl"    "https://raw.githubusercontent.com/opengeospatial/CityGML-3.0Encodings/main/CityGML/Ontologies/Core.ttl"
fetch "citygml-building.ttl" "https://raw.githubusercontent.com/opengeospatial/CityGML-3.0Encodings/main/CityGML/Ontologies/Building.ttl"
fetch "qudt-units.ttl"      "https://qudt.org/2.1/vocab/unit"
fetch "time.ttl"            "https://www.w3.org/2006/time"

upload "bot.ttl"             "https://w3id.org/bot"
upload "sosa.ttl"            "http://www.w3.org/ns/sosa/"
upload "ssn.ttl"             "http://www.w3.org/ns/ssn/"
upload "geosparql11.ttl"     "http://www.opengis.net/ont/geosparql"
upload "citygml-core.ttl"    "http://www.opengis.net/citygml/3.0/core"
upload "citygml-building.ttl" "http://www.opengis.net/citygml/3.0/building"
upload "qudt-units.ttl"      "http://qudt.org/vocab/unit"
upload "time.ttl"            "http://www.w3.org/2006/time"

echo ""
echo "=================================================="
echo "  GraphDB ready!"
echo "  UI:             ${GRAPHDB_URL}"
echo "  SPARQL endpoint: ${GRAPHDB_URL}/repositories/${REPO}"
echo "=================================================="
