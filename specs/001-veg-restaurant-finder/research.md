# Research: Veg Restaurant Finder

## Decision: Minimal Python Streamlit App
The application will be implemented as a lightweight Streamlit web app using Python 3.11+ and the smallest set of external libraries necessary: `streamlit`, `requests`, and `openai`.

## Rationale
- Streamlit Community Cloud supports Python web apps with minimal deployment overhead.
- The user requested a Streamlit app with minimal libraries and no data persistence.
- Using `requests` avoids introducing a larger HTTP framework, keeping the runtime simple.
- OpenAI will be used only for classification logic, not as the primary UI layer.

## Alternatives Considered
- Building a separate backend with Flask or FastAPI: rejected because it adds complexity and a second deployment surface.
- Persisting search results or user preferences: rejected due to the requirement that no user input or output storage is needed.
- Using a richer UI framework such as React: rejected because Streamlit is sufficient and preferred for Streamlit Community Cloud.

## Classification Approach
- Use Google Places API to search restaurants and fetch review text.
- Send relevant review text and restaurant metadata to OpenAI for a vegetarian classification decision.
- Treat results as session-only data; do not store inputs or output beyond the current page state.

## Performance & UX Notes
- Keep each search focused to limit API request volume and reduce latency.
- Show progress and user-friendly error messages when APIs return rate-limit or lookup failures.
- Apply lightweight CSS styling only to improve readability, not to create a complex UI layer.
