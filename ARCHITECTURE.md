# RouteBite Architecture

```text
backend/
├── __init__.py
│
├── main.py
|
├── schemas.py
│
├── config.py
│
├── api/
│   ├── __init__.py
│   └── recommendations.py
│
│
├── services/
│   ├── __init__.py
│   ├── recommendation_service.py
│   ├── restaurant_service.py
│   └── routing_service.py
│
└── clients/
    ├── __init__.py
    ├── google_places.py
    ├── google_routes.py
    └── osm.py
```

## `main.py`

Application entry point.

Responsibilities:

* Create the FastAPI application
* Register API routers
* Keep application startup logic minimal


## `api/recommendations.py`

HTTP/API layer for restaurant recommendations.

Responsibilities:

* Define `POST /recommendations`
* Accept and validate the request
* Call the recommendation service
* Return the response


## `schemas.py`

Defines recommendation-related Pydantic models and the normalized internal restaurant model.


## `services/recommendation_service.py`

Contains the core RouteBite ranking logic.

Responsibilities:

* Filter restaurants by dietary requirements
* Filter restaurants by minimum rating
* Filter restaurants by maximum detour
* Calculate cuisine match
* Calculate convenience score
* Calculate rating score
* Calculate final recommendation score
* Sort restaurants
* Return the top recommendations


## `services/restaurant_service.py`

Responsible for obtaining and combining restaurant information:

```text
Google Places
      ↓
Restaurant base information

OpenStreetMap
      ↓
Dietary enrichment

      ↓

Normalized Restaurant objects
```

## `services/routing_service.py`

Responsible for route-related calculations.

Responsibilities:

* Get the route between origin/current location and destination
* Determine candidate restaurant search areas
* Calculate restaurant detour time


## `clients/google_places.py`

Low-level integration with the Google Places API.

Responsibilities:

* Make HTTP requests to Google Places
* Handle Google-specific request/response formats
* Return raw or normalized place information


## `clients/osm.py`

Low-level integration with OpenStreetMap / Overpass.

Responsibilities:

* Query OSM restaurant data
* Retrieve dietary tags
* Convert OSM tags into RouteBite dietary values


---

# Request Flow

```text
Frontend
    ↓
POST /recommendations
    ↓
api/recommendations.py
    ↓
recommendation_service.py
    ↓
restaurant_service.py
    │
    ├── google_places.py
    │
    └── osm.py
    │
    ↓
routing_service.py
    ↓
filter + score + rank
    ↓
Top restaurant recommendations
    ↓
Frontend
```

# Responsibility Summary

| Layer       | Responsibility                            |
| ----------- | ----------------------------------------- |
| `main.py`   | Start/configure FastAPI                   |
| `api/`      | HTTP endpoints                            |
| `schemas/`  | Request, response, and domain data models |
| `services/` | Application/business logic                |
| `clients/`  | External API communication                |
| `config.py` | Configuration and environment settings    |

The main architectural rule is:

```text
API layer
    ↓
Service layer
    ↓
Client/external systems
```
