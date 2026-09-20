# API

Base URL: `http://localhost:8000/api/v1`

The live routes return direct JSON bodies, not an envelope. FastAPI publishes the generated contract at `/openapi.json`, with interactive UIs at `/docs` and `/redoc`.

## Authentication

Authentication and authorization are not implemented. Requests identify a user with a UUID where required. The frontend defaults to the seeded demo user `89d4a21e-b315-515f-8ff3-80b56e85ed6c`.

## Endpoints

### Health

`GET /health`

No parameters.

Example response:

```json
{"status":"ok","database":"ok","version":"0.1.0"}
```

If the database query fails, `status` is `degraded` and `database` is `unavailable`.

### Interest analysis

`POST /interests/analyze`

Request body:

```json
{"text":"I enjoy photography and building websites"}
```

`text` must be 3-2,000 non-blank characters. Example response:

```json
{
  "original_text":"I enjoy photography and building websites",
  "interests":[
    {"name":"photography","category":"Creative","confidence":0.9},
    {"name":"web development","category":"Technology","confidence":0.78}
  ],
  "goals":["create"],
  "traits":["creative"],
  "preferences":[],
  "source":"ai"
}
```

`source` is `ai` or `fallback`.

### Groups

- `GET /groups?category=&search=&interest=&page=1&page_size=20`
- `GET /groups/{group_id}`

`group_id` is a UUID. `page` must be at least 1 and `page_size` is 1-100. The list response is an array of group summaries. Each summary contains `id`, `name`, `description`, `category`, optional `image_url`, `location`, `meeting_frequency`, and `member_count`. Detail adds `interests` and `upcoming_events`.

### Events

- `GET /events?group_id=&category=&search=&from_date=&to_date=&page=1&page_size=20`
- `GET /events/{event_id}`

`group_id` and `event_id` are UUIDs. Dates are ISO datetime values. List responses are arrays of event summaries with `id`, `group_id`, `title`, `description`, `starts_at`, optional `ends_at`, `location`, optional `capacity`, and optional `image_url`. Detail adds the group, interests, and related events.

### Recommendations

`POST /recommendations`

Request body:

```json
{
  "user_id":"89d4a21e-b315-515f-8ff3-80b56e85ed6c",
  "interest_text":"I enjoy photography and meeting new people",
  "limit":10
}
```

`user_id` is optional; `interest_text` is 3-2,000 characters; `limit` is 1-50 and defaults to 10. A successful response is:

```json
{
  "recommendations":[
    {
      "id":"00000000-0000-0000-0000-000000000001",
      "type":"group",
      "target_type":"group",
      "target_id":"00000000-0000-0000-0000-000000000002",
      "title":"Example community",
      "description":"Example description",
      "score":82.4,
      "matched_interests":["photography"],
      "matched_goals":["meet_people"],
      "reasons":["Matched interests: photography","Semantic relevance: 0.81"],
      "explanation":"Matches photography; supports meet people; semantic relevance 0.81"
    }
  ]
}
```

The UUIDs and content in this example are placeholders. Use returned IDs for feedback.

### Icebreakers

`POST /icebreakers`

Request body:

```json
{
  "user_id":"89d4a21e-b315-515f-8ff3-80b56e85ed6c",
  "target_type":"group",
  "target_id":"00000000-0000-0000-0000-000000000002",
  "style":"casual"
}
```

`target_type` is `group` or `event`; `style` is `casual`, `friendly`, or `professional`. Response:

```json
{"icebreaker":"I saw you're interested in photography too. Are you joining this group?","style":"casual"}
```

The generated text is limited to 280 characters by the AI response schema.

### Profiles

- `GET /profile/{user_id}`
- `PUT /profile/{user_id}`

Update body fields are optional and limited to `name`, `bio`, `interests`, and `goals`:

```json
{"name":"Maya Shah","bio":"Photography and short films.","interests":["Photography"],"goals":["create"]}
```

The response contains `user`, weighted `interests`, `goals`, derived `traits`, `saved_groups`, and `interested_events`.

### Feedback

`POST /feedback` returns `201`.

```json
{
  "user_id":"89d4a21e-b315-515f-8ff3-80b56e85ed6c",
  "recommendation_id":"00000000-0000-0000-0000-000000000001",
  "feedback_type":"interested"
}
```

Allowed feedback types are `interested`, `not_interested`, `already_joined`, and `wrong_match`. Response:

```json
{"accepted":true,"feedback_type":"interested"}
```

Duplicate feedback of the same type for the same user/recommendation returns `409`. `interested` and `wrong_match` adjust relevant existing interest weights by bounded deterministic deltas.

## Errors

FastAPI validation and explicit route errors use:

```json
{"detail":"Human-readable error message"}
```

Common statuses:

- `404`: missing user, group, event, or recommendation.
- `409`: duplicate feedback.
- `422`: invalid UUID, enum, field length, date, or unexpected body field.
- `429`: in-memory rate limit exceeded for interest analysis, recommendations, or icebreakers.
- `502`: provider or unexpected recommendation failure.
- `503`: recommendation storage unavailable.
- `500`: generic unexpected exception response.
