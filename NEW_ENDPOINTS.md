# Scenario and Delta Storage Endpoints

Base URL: `http://localhost:8001` (Docker) or `http://localhost:8000` (manual)
API prefix: `/api/v1/vector`

---

## Overview

These endpoints support creating new scenarios from a baseline and storing only modified building properties (delta storage). The baseline scenario is identified by `scenario_id == project_id` or `scenario_name = 'baseline'`.

---

## 1. POST Create Scenario

Create a new scenario for a project based on the baseline scenario. The new scenario receives a new UUID and copies project metadata (boundary, center, etc.) from the baseline.

**Request**

```
POST /api/v1/vector/projects/{project_id}/scenarios
Content-Type: application/json
```

**Path parameters**

| Parameter   | Type   | Description |
|-------------|--------|-------------|
| project_id  | string | Project UUID |

**Body**

```json
{
  "scenario_name": "Scenario 2025"
}
```

| Field          | Type   | Required | Description                    |
|----------------|--------|----------|--------------------------------|
| scenario_name  | string | Yes      | Human-readable scenario name   |

**Example**

```bash
curl -X POST "http://localhost:8001/api/v1/vector/projects/a06ded75-705c-49a7-a14f-e6535bf1bb15/scenarios" \
  -H "Content-Type: application/json" \
  -d '{"scenario_name": "Scenario 2025"}'
```

**Response**

```json
{
  "project_id": "a06ded75-705c-49a7-a14f-e6535bf1bb15",
  "scenario_id": "7bf6aaac-f341-40ca-9c91-8e0b3f97bb8f",
  "project_name": "My Project",
  "scenario_name": "Scenario 2025",
  "project_zoom": 15,
  "project_crs": 4326,
  "created_at": "2026-02-25T12:00:00Z",
  "updated_at": "2026-02-25T12:00:00Z",
  "project_boundary": { "type": "Polygon", "coordinates": [...] },
  "project_center": { "type": "Point", "coordinates": [7.675, 45.068] }
}
```

**Errors**

| Code | Condition |
|------|-----------|
| 400 | scenario_name missing or empty |
| 404 | Project not found or baseline scenario missing |

---

## 2. PUT Upsert Building Properties

Store or update modified building properties for a non-baseline scenario (delta storage). Only modified fields need to be sent; NULL in delta means inherit from baseline. Rejects for baseline scenario (`scenario_id == project_id`).

**Request**

```
PUT /api/v1/vector/projects/{project_id}/scenarios/{scenario_id}/buildingproperties
Content-Type: application/json
```

**Path parameters**

| Parameter   | Type   | Description |
|-------------|--------|-------------|
| project_id  | string | Project UUID |
| scenario_id | string | Scenario UUID (must not be baseline) |

**Body (single modification)**

```json
{
  "building_id": "004b8df0-30bf-40da-84a1-270abc5ee33b",
  "lod": 0,
  "height": 25.5,
  "n_people": 10
}
```

**Body (batch modifications)**

```json
{
  "modifications": [
    {
      "building_id": "004b8df0-30bf-40da-84a1-270abc5ee33b",
      "lod": 0,
      "height": 25.5,
      "n_people": 10
    },
    {
      "building_id": "another-building-uuid",
      "lod": 0,
      "area": 500,
      "volume": 12000
    }
  ]
}
```

**Editable fields**

| Field               | Type   | Description |
|---------------------|--------|-------------|
| height              | float  | Building height |
| area                | float  | Footprint area |
| volume              | float  | Building volume |
| number_of_floors    | float  | Number of floors |
| type                | string | Building type |
| const_period_census | string | Construction period (census) |
| const_year          | int    | Construction year |
| const_tabula        | string | TABULA classification |
| n_people            | int    | Number of people |
| n_family            | int    | Number of families |

**Example**

```bash
curl -X PUT "http://localhost:8001/api/v1/vector/projects/a06ded75-705c-49a7-a14f-e6535bf1bb15/scenarios/7bf6aaac-f341-40ca-9c91-8e0b3f97bb8f/buildingproperties" \
  -H "Content-Type: application/json" \
  -d '{"building_id": "004b8df0-30bf-40da-84a1-270abc5ee33b", "lod": 0, "height": 300, "n_people": 100}'
```

**Response**

```json
{
  "upserted": 1,
  "scenario_id": "7bf6aaac-f341-40ca-9c91-8e0b3f97bb8f"
}
```

**Errors**

| Code | Condition |
|------|-----------|
| 400 | Baseline scenario or missing building_id or no editable fields |
| 404 | Scenario not found |

---

## 3. GET Buildings GeoJSON (with Merged Delta)

Get all buildings for a project scenario as GeoJSON FeatureCollection. For baseline scenarios, a single query is used. For non-baseline, baseline and delta are merged in memory (baseline overwritten by non-NULL delta values).

**Request**

```
GET /api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}?lod=0
```

**Path parameters**

| Parameter   | Type   | Description |
|-------------|--------|-------------|
| project_id  | string | Project UUID |
| scenario_id | string | Scenario UUID |

**Query parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| lod       | int  | 0       | Level of detail |

**Example**

```bash
curl -X GET "http://localhost:8001/api/v1/vector/get_buildings_geojson/a06ded75-705c-49a7-a14f-e6535bf1bb15/7bf6aaac-f341-40ca-9c91-8e0b3f97bb8f?lod=0"
```

**Response**

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[7.67, 45.06], [7.68, 45.06], [7.68, 45.07], [7.67, 45.07], [7.67, 45.06]]]
      },
      "properties": {
        "building_id": "004b8df0-30bf-40da-84a1-270abc5ee33b",
        "lod": 0,
        "height": 300,
        "area": 545.43,
        "volume": 12212.22,
        "type": "residential",
        "n_people": 100,
        "n_family": 3,
        "number_of_floors": 7,
        "const_year": 1995,
        "const_period_census": "E14",
        "const_tabula": "TABULA_7"
      }
    }
  ]
}
```

---

## 4. GET Building Properties (with Merged Delta)

Query building properties for a project scenario. Same merge logic as GeoJSON: baseline only for baseline scenario; baseline + delta merge for non-baseline.

**Request**

```
GET /api/v1/vector/buildingproperties/{project_id}/{scenario_id}?lod=0&building_id=&limit=100&offset=0
```

**Path parameters**

| Parameter   | Type   | Description |
|-------------|--------|-------------|
| project_id  | string | Project UUID |
| scenario_id | string | Scenario UUID |

**Query parameters**

| Parameter   | Type   | Default | Description |
|-------------|--------|---------|-------------|
| building_id | string | -       | Filter by building |
| lod         | int    | 0       | Level of detail |
| limit       | int    | 100     | Max results |
| offset      | int    | 0       | Pagination offset |

**Example**

```bash
curl -X GET "http://localhost:8001/api/v1/vector/buildingproperties/a06ded75-705c-49a7-a14f-e6535bf1bb15/7bf6aaac-f341-40ca-9c91-8e0b3f97bb8f?lod=0"
```

---

## Delta Storage Behavior

- Baseline scenario: full rows in `cim_wizard_building_properties` for all buildings.
- Non-baseline scenario: only rows for buildings with changes; only modified columns are stored.
- GET merge: baseline values are overwritten by non-NULL delta values per building.
- Baseline is resolved by: `scenario_id == project_id` first, else `scenario_name = 'baseline'`.

---

## Typical Workflow

1. `GET /api/v1/vector/projects` - list projects
2. `GET /api/v1/vector/pscenarios/{project_id}` - list scenarios
3. `POST /api/v1/vector/projects/{project_id}/scenarios` - create new scenario
4. `PUT /api/v1/vector/projects/{project_id}/scenarios/{scenario_id}/buildingproperties` - store modifications
5. `GET /api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}` - get merged GeoJSON
