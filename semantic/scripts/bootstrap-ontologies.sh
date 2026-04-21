#!/bin/sh
# ============================================================
#  bootstrap-ontologies.sh
#  Downloads all geospatial/building ontologies and loads them
#  into Apache Jena Fuseki as named graphs.
# ============================================================

set -e

FUSEKI_URL="${FUSEKI_URL:-http://localhost:3030}"
DATASET="${DATASET:-geo}"
PASSWORD="${FUSEKI_ADMIN_PASSWORD:-admin123}"
ONT_DIR="/ontologies"
BASE_URL="${FUSEKI_URL}/${DATASET}/data"

echo "=================================================="
echo "  Bootstrapping ontologies into ${FUSEKI_URL}/${DATASET}"
echo "=================================================="

# ── Helper: download if not already cached ─────────────────
fetch() {
  local name="$1"
  local url="$2"
  local file="${ONT_DIR}/${name}"
  if [ -f "$file" ]; then
    echo "[SKIP]  $name already cached"
  else
    echo "[DL]    $name"
    curl -sL --retry 3 -o "$file" "$url" \
      && echo "[OK]    Downloaded $name" \
      || echo "[WARN]  Failed to download $name — skipping"
  fi
}

# ── Helper: upload TTL file as a named graph ───────────────
upload() {
  local name="$1"
  local file="${ONT_DIR}/$name"
  local graph="$2"
  if [ ! -f "$file" ]; then
    echo "[SKIP]  $name not found, skipping upload"
    return
  fi
  echo "[LOAD]  $name → <$graph>"
  curl -sf -u "admin:${PASSWORD}" \
    -X PUT \
    -H "Content-Type: text/turtle" \
    --data-binary "@${file}" \
    "${BASE_URL}?graph=${graph}" \
    && echo "[OK]    Loaded $name" \
    || echo "[WARN]  Failed to load $name"
}

# ══════════════════════════════════════════════════════════
#  1. GeoSPARQL 1.0  (OGC) — spatial primitives & functions
# ══════════════════════════════════════════════════════════
fetch "geosparql.ttl" \
  "https://schemas.opengis.net/geosparql/1.0/geosparql_vocab_all.rdf"

upload "geosparql.ttl" \
  "http://www.opengis.net/ont/geosparql"

# ══════════════════════════════════════════════════════════
#  2. BOT — Building Topology Ontology (W3C LBD)
#     Covers Zone, Building, Storey, Space, Element
# ══════════════════════════════════════════════════════════
fetch "bot.ttl" \
  "https://raw.githubusercontent.com/w3c-lbd-cg/bot/master/bot.ttl"

upload "bot.ttl" \
  "https://w3id.org/bot"

# ══════════════════════════════════════════════════════════
#  3. SOSA / SSN — Sensor & Actuator ontology (W3C)
#     Covers Sensor, Observation, FeatureOfInterest
# ══════════════════════════════════════════════════════════
fetch "sosa.ttl" \
  "https://www.w3.org/ns/sosa/"

fetch "ssn.ttl" \
  "https://www.w3.org/ns/ssn/"

upload "sosa.ttl" \
  "http://www.w3.org/ns/sosa/"

upload "ssn.ttl" \
  "http://www.w3.org/ns/ssn/"

# ══════════════════════════════════════════════════════════
#  4. OWL Time — temporal coverage for observations
# ══════════════════════════════════════════════════════════
fetch "time.ttl" \
  "https://www.w3.org/2006/time"

upload "time.ttl" \
  "http://www.w3.org/2006/time"

# ══════════════════════════════════════════════════════════
#  5. GeoSPARQL 1.1 (OGC, 2022) — extended geometry support
# ══════════════════════════════════════════════════════════
fetch "geosparql11.ttl" \
  "https://opengeospatial.github.io/ogc-geosparql/geosparql11/geo.ttl"

upload "geosparql11.ttl" \
  "http://www.opengis.net/ont/geosparql11"

# ══════════════════════════════════════════════════════════
#  6. CityGML 3.0 OWL (OGC) — conceptual model only
#     Full encoding: https://github.com/opengeospatial/CityGML-3.0Encodings
# ══════════════════════════════════════════════════════════
fetch "citygml-core.ttl" \
  "https://raw.githubusercontent.com/opengeospatial/CityGML-3.0Encodings/main/CityGML/Ontologies/Core.ttl"

fetch "citygml-building.ttl" \
  "https://raw.githubusercontent.com/opengeospatial/CityGML-3.0Encodings/main/CityGML/Ontologies/Building.ttl"

fetch "citygml-construction.ttl" \
  "https://raw.githubusercontent.com/opengeospatial/CityGML-3.0Encodings/main/CityGML/Ontologies/Construction.ttl"

upload "citygml-core.ttl" \
  "http://www.opengis.net/citygml/3.0/core"

upload "citygml-building.ttl" \
  "http://www.opengis.net/citygml/3.0/building"

upload "citygml-construction.ttl" \
  "http://www.opengis.net/citygml/3.0/construction"

# ══════════════════════════════════════════════════════════
#  7. QUDT — units of measure (height, area, volume…)
# ══════════════════════════════════════════════════════════
fetch "qudt-units.ttl" \
  "https://qudt.org/2.1/vocab/unit"

upload "qudt-units.ttl" \
  "http://qudt.org/vocab/unit"

echo ""
echo "=================================================="
echo "  Bootstrap complete."
echo "  SPARQL endpoint: ${FUSEKI_URL}/${DATASET}/sparql"
echo "  Named graphs loaded:"
curl -sf -u "admin:${PASSWORD}" \
  -H "Accept: application/sparql-results+json" \
  "${FUSEKI_URL}/${DATASET}/sparql?query=SELECT+DISTINCT+%3Fg+WHERE+%7BGRAPH+%3Fg+%7B%7D%7D" \
  | grep -o '"value":"[^"]*"' | grep -v "value.*http://www.w3.org/2001/XMLSchema" \
  | sed 's/"value":"//;s/"//'
echo "=================================================="
