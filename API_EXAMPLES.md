# CIM Wizard API Examples

Base URL: `http://localhost:8000`
API prefix: `/api/v1`

---

## 1. Get Projects

List all projects with pagination.

**Request**

```
GET /api/v1/vector/projects?limit=100&offset=0
```

**Query parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | int | 100 | Max number of projects (1–1000) |
| offset | int | 0 | Number of projects to skip |

**Example (curl)**

```bash
curl -X GET "http://localhost:8000/api/v1/vector/projects?limit=10&offset=0"
```

**Example response**

```json
[
  {
    "project_id": "0c1115d7-8fe3-4f73-8c91-fb387bdcb582",
    "scenario_id": "3b933821-eee3-4544-90e1-7f4f188fcbff",
    "project_name": "pietro_test",
    "scenario_name": "baseline",
    "project_zoom": 15,
    "project_crs": 4326,
    "created_at": "2026-02-13T13:27:42.100189+00:00",
    "updated_at": "2026-02-13T13:27:43.556267+00:00",
    "project_boundary": {
      "type": "Polygon",
      "coordinates": [[[7.67, 45.06], [7.67, 45.07], [7.68, 45.07], [7.67, 45.06]]]
    },
    "project_center": {
      "type": "Point",
      "coordinates": [7.675, 45.068]
    }
  }
]
```

---

## 2. Get Project's Scenarios

List all scenarios for a given project.

**Request**

```
GET /api/v1/vector/pscenarios/{project_id}
```

**Path parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | Project UUID |

**Example (curl)**

```bash
curl -X GET "http://localhost:8000/api/v1/vector/pscenarios/0c1115d7-8fe3-4f73-8c91-fb387bdcb582"
```

**Example response**

```json
[
  {
    "project_id": "0c1115d7-8fe3-4f73-8c91-fb387bdcb582",
    "scenario_id": "3b933821-eee3-4544-90e1-7f4f188fcbff",
    "project_name": "pietro_test",
    "scenario_name": "baseline",
    "project_zoom": 15,
    "project_crs": 4326,
    "created_at": "2026-02-13T13:27:42.100189+00:00",
    "updated_at": "2026-02-13T13:27:43.556267+00:00",
    "project_boundary": { "type": "Polygon", "coordinates": [...] },
    "project_center": { "type": "Point", "coordinates": [7.675, 45.068] }
  }
]
```

---

## 3. Get Project-Scenario's Buildings

Get all buildings for a project scenario as GeoJSON FeatureCollection.

**Request**

```
GET /api/v1/vector/get_buildings_geojson/{project_id}/{scenario_id}?lod=0
```

**Path parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| project_id | string | Project UUID |
| scenario_id | string | Scenario UUID |

**Query parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| lod | int | 0 | Level of detail |

**Example (curl)**

```bash
curl -X GET "http://localhost:8000/api/v1/vector/get_buildings_geojson/0c1115d7-8fe3-4f73-8c91-fb387bdcb582/3b933821-eee3-4544-90e1-7f4f188fcbff"
```

**Example response**

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
        "building_id": "0f9d5e66-59d9-4a20-bfdf-ad65ddfba30b",
        "lod": 0,
        "height": 19.08,
        "area": 456.87,
        "volume": 8717.04,
        "type": "residential",
        "n_people": 7,
        "n_family": 3,
        "number_of_floors": 6,
        "const_year": 1975,
        "const_period_census": "E12"
      }
    }
  ]
}
```

---

## 4. POST New Project by Project Boundary

Create a new project and run the full building analysis pipeline (16 steps). The project boundary must be a GeoJSON Polygon in EPSG:4326.

**Request**

```
POST /api/v1/building/execute_building_analysis
Content-Type: application/json
```

**Body**

```json
{
  "project_boundary": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [7.671331210498124, 45.066213066884785],
          [7.674764438037698, 45.071426259580136],
          [7.677682681445418, 45.07057763270552],
          [7.673734469776463, 45.06512187335625],
          [7.671331210498124, 45.066213066884785]
        ]
      ]
    },
    "properties": {}
  },
  "project_name": "My Project",

  "save_to_db": true
}
```

**Body parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| project_boundary | GeoJSON Feature or FeatureCollection | Yes | — | Polygon boundary in EPSG:4326 |
| project_name | string | No | "Building_Analysis" | Human-readable project name |
| scenario_name | string | No | "baseline" | Scenario name (null → "baseline") |
| save_to_db | boolean | No | true | Persist results to database |

**Example (curl)**

```bash
curl -X POST "http://localhost:8000/api/v1/building/execute_building_analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "project_boundary": {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[7.671, 45.066], [7.675, 45.071], [7.678, 45.071], [7.674, 45.065], [7.671, 45.066]]]
      },
      "properties": {}
    },
    "project_name": "pietro_test",

    "save_to_db": true
  }'
```

**Example response (excerpt)**

```json
{
  "project_id": "1e2e3502-a25b-4984-b42e-768dc8d097b9",
  "scenario_id": "1e2e3502-a25b-4984-b42e-768dc8d097b9",
  "project_name": "pietro_test",
  "scenario_name": "baseline",
  "successful_calculations": ["scenario_geo", "scenario_census_boundary", "building_geo", ...],
  "summary": {
    "total_buildings": 249,
    "residential_buildings": 180,
    "census_population": 1200.0
  },
  "metadata": {
    "success_rate": "100.0%",
    "pipeline_version": "2.0.0"
  }
}
```

---

## 5. Delete Specific Building

Delete one building from a project scenario.

**Request**

```
DELETE /api/v1/vector/delete?project_id={project_id}&scenario_id={scenario_id}&building_id={building_id}
```

**Query parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project_id | string | Yes | Project UUID |
| scenario_id | string | Yes | Scenario UUID |
| building_id | string | Yes | Building UUID |

**Example (curl)**

```bash
curl -X DELETE "http://localhost:8000/api/v1/vector/delete?project_id=0c1115d7-8fe3-4f73-8c91-fb387bdcb582&scenario_id=3b933821-eee3-4544-90e1-7f4f188fcbff&building_id=0f9d5e66-59d9-4a20-bfdf-ad65ddfba30b"
```

**Example response**

```json
{
  "action": "delete_building",
  "project_id": "0c1115d7-8fe3-4f73-8c91-fb387bdcb582",
  "scenario_id": "3b933821-eee3-4544-90e1-7f4f188fcbff",
  "building_id": "0f9d5e66-59d9-4a20-bfdf-ad65ddfba30b",
  "building_properties_deleted": 1,
  "buildings_deleted": 1,
  "project_scenarios_deleted": 0
}
```

---

## 6. Delete Specific Scenario

Delete a scenario and all its buildings.

**Request**

```
DELETE /api/v1/vector/delete?project_id={project_id}&scenario_id={scenario_id}
```

**Query parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project_id | string | Yes | Project UUID |
| scenario_id | string | Yes | Scenario UUID |

**Example (curl)**

```bash
curl -X DELETE "http://localhost:8000/api/v1/vector/delete?project_id=0c1115d7-8fe3-4f73-8c91-fb387bdcb582&scenario_id=3b933821-eee3-4544-90e1-7f4f188fcbff"
```

**Example response**

```json
{
  "action": "delete_scenario",
  "project_id": "0c1115d7-8fe3-4f73-8c91-fb387bdcb582",
  "scenario_id": "3b933821-eee3-4544-90e1-7f4f188fcbff",
  "building_properties_deleted": 249,
  "buildings_deleted": 249,
  "project_scenarios_deleted": 1
}
```

---

## 7. Delete Specific Project

Delete an entire project (all scenarios and buildings).

**Request**

```
DELETE /api/v1/vector/delete?project_id={project_id}
```

**Query parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| project_id | string | Yes | Project UUID |

**Example (curl)**

```bash
curl -X DELETE "http://localhost:8000/api/v1/vector/delete?project_id=0c1115d7-8fe3-4f73-8c91-fb387bdcb582"
```

**Example response**

```json
{
  "action": "delete_project",
  "project_id": "0c1115d7-8fe3-4f73-8c91-fb387bdcb582",
  "scenarios_affected": ["3b933821-eee3-4544-90e1-7f4f188fcbff"],
  "building_properties_deleted": 249,
  "buildings_deleted": 249,
  "project_scenarios_deleted": 1
}
```

---

## Postman Quick Reference

| # | Method | URL |
|---|--------|-----|
| 1 | GET | `{{base}}/api/v1/vector/projects?limit=100&offset=0` |
| 2 | GET | `{{base}}/api/v1/vector/pscenarios/{{project_id}}` |
| 3 | GET | `{{base}}/api/v1/vector/get_buildings_geojson/{{project_id}}/{{scenario_id}}` |
| 4 | POST | `{{base}}/api/v1/building/execute_building_analysis` |
| 5 | DELETE | `{{base}}/api/v1/vector/delete?project_id={{project_id}}&scenario_id={{scenario_id}}&building_id={{building_id}}` |
| 6 | DELETE | `{{base}}/api/v1/vector/delete?project_id={{project_id}}&scenario_id={{scenario_id}}` |
| 7 | DELETE | `{{base}}/api/v1/vector/delete?project_id={{project_id}}` |

Set `base` to `http://localhost:8000` (or your backend host).
