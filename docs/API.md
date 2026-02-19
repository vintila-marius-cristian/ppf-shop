# API Endpoints

## 1) Event Tracking
- **URL:** `/api/track/`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Purpose:** Store user interactions for custom analytics.

### Request body
```json
{
  "event_type": "cta_click",
  "element": "hero_contact",
  "page": "/",
  "session_id": "1708351123-abcd1234",
  "additional_data": {
    "depth": 72
  }
}
```

### Success response
- **Status:** `201 Created`
```json
{
  "status": "tracked"
}
```

## 2) Contact Submission API
- **URL:** `/api/contact/`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Purpose:** Validate and persist contact inquiries, trigger notification email.

### Request body
```json
{
  "name": "Ion Popescu",
  "email": "ion@example.com",
  "phone": "+40740111222",
  "subject": "Cerere oferta",
  "message": "As dori o oferta pentru PPF partial."
}
```

### Success response
- **Status:** `201 Created`
```json
{
  "status": "ok",
  "id": 12
}
```

## 3) Blog API (read-only)
- **URL:** `/api/blog/posts/`
- **Method:** `GET`
- **Purpose:** Retrieve published blog entries for optional client-side rendering.

### Example response
```json
[
  {
    "title": "Cum alegi corect PPF pentru masina ta in Pitesti",
    "slug": "cum-alegi-corect-ppf",
    "author": "Echipa Premiere Aesthetics",
    "summary": "Ghid practic pentru alegerea foliei PPF...",
    "content": "PPF este una dintre cele mai eficiente...",
    "published_at": "2026-02-19T18:00:00Z",
    "categories": ["PPF"],
    "tags": ["pitesti", "protectie auto"],
    "reading_time_minutes": 2
  }
]
```
