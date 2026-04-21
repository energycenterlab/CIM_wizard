# Triple Store Stack — CityGML + GeoSPARQL

```
triple-store/
├── docker-compose.yml          ← main compose (profiles: fuseki | graphdb)
├── .env                        ← passwords / config
├── fuseki/
│   └── config/
│       └── geo.ttl             ← Fuseki dataset config with GeoSPARQL
├── graphdb/
│   └── config/                 ← GraphDB repo configs (auto-created)
├── ontologies/                 ← TTL files downloaded & cached here
├── scripts/
│   ├── bootstrap-ontologies.sh ← downloads + loads into Fuseki
│   └── bootstrap-graphdb.sh    ← downloads + loads into GraphDB
├── sample-queries.sparql       ← test queries you can paste into the UI
└── triple_client.py            ← Python helper for FastAPI
```

---

## Quick Start

### Option A — Fuseki (recommended for development)

```bash
docker compose --profile fuseki up -d
```

- UI:             http://localhost:3030  (admin / admin123)
- SPARQL query:   http://localhost:3030/geo/sparql
- SPARQL update:  http://localhost:3030/geo/update

On first start the `fuseki-init` container downloads and loads all
ontologies automatically. Check progress with:

```bash
docker logs -f fuseki-init
```

### Option B — GraphDB

```bash
docker compose --profile graphdb up -d
```

- UI:             http://localhost:7200
- SPARQL endpoint: http://localhost:7200/repositories/citygml

---

## Ontologies Pre-loaded

| Named Graph | Ontology |
|---|---|
| `http://www.opengis.net/ont/geosparql` | GeoSPARQL 1.0 |
| `http://www.opengis.net/ont/geosparql11` | GeoSPARQL 1.1 |
| `https://w3id.org/bot` | BOT — Building Topology |
| `http://www.w3.org/ns/sosa/` | SOSA — Sensors |
| `http://www.w3.org/ns/ssn/` | SSN — Sensor Network |
| `http://www.w3.org/2006/time` | OWL Time |
| `http://www.opengis.net/citygml/3.0/core` | CityGML 3.0 Core |
| `http://www.opengis.net/citygml/3.0/building` | CityGML 3.0 Building |
| `http://qudt.org/vocab/unit` | QUDT Units |

---

## Adding Your Own Ontology

1. Drop your `.ttl` file into `ontologies/`
2. Add it to `scripts/bootstrap-ontologies.sh`:

```sh
upload "my-extension.ttl" "http://example.org/my-extension"
```

3. Re-run the init container:
```bash
docker compose --profile fuseki run --rm fuseki-init
```

---

## Python Integration

```python
from triple_client import sparql_select

buildings = sparql_select("""
    PREFIX bot: <https://w3id.org/bot#>
    SELECT ?b WHERE { ?b a bot:Building }
""")
```

---

## Notes on Pre-Populated Docker Images

There is **no widely-distributed public Docker image** pre-loaded with
CityGML OWL + GeoSPARQL + BOT — these are schema/vocabulary ontologies,
not datasets, so they are always bootstrapped fresh. The `fuseki-init`
container here fills that gap: it downloads, caches, and loads them on
first boot, and the `ontologies/` folder acts as a persistent cache so
restarts are instant.
