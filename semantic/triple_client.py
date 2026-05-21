"""
triple_client.py
================
Reusable helper for querying your Fuseki / GraphDB triple store
from FastAPI or any Python script.

Install:
    pip install rdflib SPARQLWrapper requests
"""

from __future__ import annotations
import json
from typing import Any
from SPARQLWrapper import SPARQLWrapper, JSON, POST, TURTLE


# ── Configuration ────────────────────────────────────────────
FUSEKI   = "http://localhost:3030/geo"
GRAPHDB  = "http://localhost:7200/repositories/citygml"

# Pick your backend
ENDPOINT       = FUSEKI + "/sparql"
UPDATE_ENDPOINT = FUSEKI + "/update"


# ── SPARQL SELECT ────────────────────────────────────────────
def sparql_select(query: str, endpoint: str = ENDPOINT) -> list[dict[str, Any]]:
    """Execute a SELECT query; return list of row dicts."""
    sw = SPARQLWrapper(endpoint)
    sw.setQuery(query)
    sw.setReturnFormat(JSON)
    results = sw.query().convert()
    rows = []
    for r in results["results"]["bindings"]:
        rows.append({k: v["value"] for k, v in r.items()})
    return rows


# ── SPARQL UPDATE (INSERT/DELETE) ────────────────────────────
def sparql_update(update: str, endpoint: str = UPDATE_ENDPOINT) -> None:
    """Execute a SPARQL Update (INSERT DATA, DELETE …)."""
    sw = SPARQLWrapper(endpoint)
    sw.setMethod(POST)
    sw.setQuery(update)
    sw.query()


# ── Load a local TTL file as a named graph ───────────────────
def load_turtle_file(
    ttl_path: str,
    named_graph: str,
    fuseki_data_endpoint: str = FUSEKI + "/data",
    password: str = "admin123",
) -> None:
    import requests
    with open(ttl_path, "rb") as f:
        r = requests.put(
            fuseki_data_endpoint,
            params={"graph": named_graph},
            data=f,
            headers={"Content-Type": "text/turtle"},
            auth=("admin", password),
        )
        r.raise_for_status()
    print(f"Loaded {ttl_path} → <{named_graph}>")


# ── FastAPI dependency example ───────────────────────────────
# from fastapi import Depends
#
# def get_sparql():
#     return lambda q: sparql_select(q)
#
# @router.get("/buildings")
# def list_buildings(sparql=Depends(get_sparql)):
#     return sparql("""
#         PREFIX bot: <https://w3id.org/bot#>
#         SELECT ?b WHERE { ?b a bot:Building }
#     """)


# ── Quick sanity check ───────────────────────────────────────
if __name__ == "__main__":
    graphs = sparql_select(
        "SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } } ORDER BY ?g"
    )
    print("Named graphs loaded:")
    for g in graphs:
        print(f"  {g['g']}")