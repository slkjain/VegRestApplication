# API Integration Contract

## Purpose
Define the contract for the external APIs used by the vegetarian restaurant search app.

## Google Places API Contract

### Search Request
- Endpoint: `https://maps.googleapis.com/maps/api/place/textsearch/json`
- Query parameters:
  - `query`: user location or search term
  - `type`: `restaurant`
  - `key`: `GOOGLE_API_KEY`
  - optional `location` and `radius` as available

### Search Response
- Must include a list of place results, each containing:
  - `place_id`
  - `name`
  - `formatted_address`
  - `rating`
  - optional `types`

### Review Request
- Endpoint: `https://maps.googleapis.com/maps/api/place/details/json`
- Query parameters:
  - `place_id`: place identifier
  - `fields`: `review` or `reviews`
  - `key`: `GOOGLE_API_KEY`

### Review Response
- Must include `reviews`, where each review contains:
  - `author_name`
  - `rating`
  - `relative_time_description`
  - `text`

## OpenAI Classification Contract

### Input
- Use the OpenAI completions or responses API with an instruction prompt.
- Supply a payload containing:
  - restaurant name and address
  - relevant review excerpts or aggregated sentiment
  - explicit task: determine whether the restaurant is pure vegetarian

### Output
- A structured text response that resolves to one of:
  - `Pure Vegetarian`
  - `Not Pure Vegetarian`
  - `Unknown`
- The app maps the response to `is_pure_vegetarian` boolean.

## Environment Variables
- `GOOGLE_API_KEY`: API key for Google Places and details requests
- `OPENAI_API_KEY`: API key for OpenAI classification calls

## Error Handling
- If Google or OpenAI returns an error, the app must display a user-friendly message.
- If classification returns ambiguous results, the app should mark the restaurant as `Unknown` and prompt the user accordingly.
