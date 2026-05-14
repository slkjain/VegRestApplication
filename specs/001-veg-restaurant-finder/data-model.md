# Data Model: Veg Restaurant Finder

## Entities

### Restaurant
- `id`: String, unique identifier from Google Places.
- `name`: String, restaurant name.
- `address`: String, formatted address.
- `rating`: Float, average rating from Google.
- `is_pure_vegetarian`: Boolean, OpenAI classification result.
- `review_snippet`: String, representative excerpt from reviews used for classification.
- `reviews`: List of `Review` objects (optional, runtime only).

### Review
- `author_name`: String, reviewer name.
- `rating`: Integer, review rating.
- `relative_time_description`: String, time since review.
- `text`: String, review content used for classification.

## Relationships
- A `Restaurant` may include multiple `Review` objects.
- `Review` is a runtime detail attached to a single `Restaurant`.

## Validation Rules
- `Restaurant.id` MUST be present for any restaurant object returned from Google.
- `Restaurant.name` and `address` MUST be present for display.
- `is_pure_vegetarian` MUST be set explicitly by the classification workflow.
- `Review.text` MUST be non-empty before sending content to OpenAI for classification.

## Persistence
- No persistence layer is required. All restaurant and review data is kept in-memory for the session only.
