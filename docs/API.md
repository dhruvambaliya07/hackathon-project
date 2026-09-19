# Aatmoday Connect API

Base URL: `/api/v1`

Responses use the endpoint's normal JSON body and FastAPI's standard error shape, for example `{"detail": "..."}`. The OpenAPI document is available at `/openapi.json`.

## Endpoints

### Health

`GET /health`

Returns `{ status, database, version }`. Database values are `ok` or `unavailable`.

### Interest analysis

`POST /interests/analyze`

```json
{"text": "I enjoy photography and building websites"}
```

Returns normalized interests with confidence, goals, traits, source, and original text. Text is limited to 2,000 characters. Provider failures use deterministic keyword fallback when possible.

### Groups

- `GET /groups?page=1&page_size=20&search=&category=&interest=`
- `GET /groups/{group_id}`

`page_size` is limited to 100. Group detail includes linked interests and upcoming events.

### Events

- `GET /events?page=1&page_size=20&search=&group_id=&category=&from_date=&to_date=`
- `GET /events/{event_id}`

`page_size` is limited to 100. Event detail includes its group, interests, and related events.

### Recommendations

`POST /recommendations`

```json
{
  "user_id": "89d4a21e-b315-515f-8ff3-80b56e85ed6c",
  "interest_text": "I enjoy photography",
  "limit": 10
}
```

`interest_text` is limited to 2,000 characters and `limit` is 1-50. Each result includes a persisted recommendation `id`, target type/id, score from 0-100, matched interests, reasons, and explanation. Use the persisted `id` for feedback.

### Icebreakers

`POST /icebreakers`

```json
{
  "user_id": "89d4a21e-b315-515f-8ff3-80b56e85ed6c",
  "target_type": "group",
  "target_id": "00000000-0000-0000-0000-000000000000",
  "style": "casual"
}
```

`target_type` is `group` or `event`; `style` is `casual`, `friendly`, or `professional`. Returns one short icebreaker.

### Profiles

- `GET /profile/{user_id}`
- `PUT /profile/{user_id}`

Update body:

```json
{
  "name": "Maya Shah",
  "bio": "Photography and short films.",
  "interests": ["Photography", "Writing"],
  "goals": ["create"]
}
```

The response contains `user`, weighted `interests`, `goals`, derived `traits`, `saved_groups`, and `interested_events`.

### Feedback

`POST /feedback`

```json
{
  "user_id": "89d4a21e-b315-515f-8ff3-80b56e85ed6c",
  "recommendation_id": "00000000-0000-0000-0000-000000000000",
  "feedback_type": "interested"
}
```

Allowed feedback types: `interested`, `not_interested`, `already_joined`, `wrong_match`. Duplicate feedback of the same type for one recommendation returns `409`. `interested` and `wrong_match` adjust relevant existing interest weights by bounded deterministic deltas.

## Operational responses

- `200`: successful reads and generated content
- `201`: feedback accepted
- `404`: missing user, group, event, or recommendation
- `409`: duplicate feedback
- `422`: malformed UUID, invalid enum, oversized/invalid input, or unexpected field
- `429`: in-memory provider-backed endpoint rate limit
- `502`: provider failure
- `503`: recommendation storage unavailable
