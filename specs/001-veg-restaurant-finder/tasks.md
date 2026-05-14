# Tasks: Veg Restaurant Finder

**Input**: Design documents from `/specs/001-veg-restaurant-finder/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The feature specification does not request TDD explicitly, so test tasks are not included here. Manual validation and smoke checks should still be performed as part of implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create `app.py` with the Streamlit page layout, search form, and result placeholders
- [X] T002 Create `utils/api_clients.py` with Google Places and Google Place Details helper functions
- [X] T003 Create `utils/models.py` with runtime `Restaurant` and `Review` structures and validation helpers
- [X] T004 Create `requirements.txt` listing `streamlit`, `requests`, and `openai`
- [X] T005 Create `specs/001-veg-restaurant-finder/quickstart.md` content if needed to document environment setup and local run commands

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [X] T006 Implement Google Places search integration in `utils/api_clients.py` using the Text Search API contract
- [X] T007 Implement Google Place Details review fetch in `utils/api_clients.py` using the Place Details API contract
- [X] T008 Implement OpenAI classification helper in `utils/api_clients.py` to determine `is_pure_vegetarian` from review text and metadata
- [X] T009 Implement shared API error handling and user-friendly failure messages in `utils/api_clients.py`
- [X] T010 Implement environment key handling for `GOOGLE_API_KEY` and `OPENAI_API_KEY` in `app.py`
- [X] T011 Add lightweight CSS styling and user experience polish to `app.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Search Restaurants by Location (Priority: P1)

**Goal**: Allow users to search for restaurants by location and see vegetarian status for each result.

**Independent Test**: Verify that entering a location produces restaurant results with vegetarian status displayed.

- [X] T012 [US1] Implement location search input and search button in `app.py`
- [X] T013 [US1] Wire `app.py` search actions to `utils/api_clients.py` Google Places search logic
- [X] T014 [US1] Use OpenAI classification helper in `utils/api_clients.py` to set `is_pure_vegetarian` for each restaurant
- [X] T015 [US1] Render the restaurant list in `app.py` with name, address, rating, and vegetarian status label
- [X] T016 [US1] Implement invalid input and empty-result messaging in `app.py`

**Checkpoint**: User Story 1 should be functional and independently testable.

---

## Phase 4: User Story 2 - View Restaurant Reviews (Priority: P2)

**Goal**: Allow users to view reviews for a selected restaurant.

**Independent Test**: Verify that selecting a restaurant displays its review list or a no-reviews message.

- [X] T017 [US2] Add restaurant selection or detail expansion controls in `app.py`
- [X] T018 [US2] Implement review fetch logic in `utils/api_clients.py` using the Google Place Details API contract
- [X] T019 [US2] Display review excerpts and metadata in `app.py`
- [X] T020 [US2] Show a clear fallback message when a restaurant has no available reviews in `app.py`

**Checkpoint**: User Story 2 should be functional without requiring additional storage.

---

## Phase 5: User Story 3 - Filter Vegetarian Restaurants (Priority: P3)

**Goal**: Allow users to filter search results to show only pure vegetarian restaurants.

**Independent Test**: Verify that enabling the filter shows only restaurants classified as pure vegetarian.

- [X] T021 [US3] Add a vegetarian-only filter control in `app.py`
- [X] T022 [US3] Implement filtering logic in `app.py` using `is_pure_vegetarian`
- [X] T023 [US3] Display `Unknown` classification state clearly and handle it as a separate UI state in `app.py`

**Checkpoint**: User Story 3 should be functional and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T024 [P] Refactor `app.py`, `utils/api_clients.py`, and `utils/models.py` to improve readability and reduce duplication
- [X] T025 [P] Update `specs/001-veg-restaurant-finder/quickstart.md` with exact local run commands and Streamlit Community Cloud deployment notes
- [ ] T026 [P] Validate the Streamlit app locally and confirm no user input or output is persisted beyond the session
- [X] T027 [P] Add inline comments and environment guidance for `GOOGLE_API_KEY` and `OPENAI_API_KEY` in `app.py`

---

## Dependencies & Execution Order

- **Setup (Phase 1)** must start first and establish the entrypoint and helper modules.
- **Foundational (Phase 2)** blocks all user stories until API integration and environment configuration are complete.
- **User Story 1 (P1)** can begin once Phase 2 is complete and is the MVP slice.
- **User Story 2 (P2)** and **User Story 3 (P3)** can begin after Phase 2 and should remain independently testable.
- **Polish (Phase 6)** depends on completion of the desired story work.

### Parallel Opportunities

- `T003`, `T005`, and `T025` can run in parallel as they touch different files and do not block core implementation.
- `T006`, `T007`, `T008`, and `T009` can be implemented in parallel within the foundational phase if separate team members work on different helper files.
- Once Phase 2 completes, User Stories 1, 2, and 3 can be worked on in parallel by different developers.

### Story Execution Order

- **T012–T016** implement the core search experience for User Story 1.
- **T017–T020** add review details for User Story 2.
- **T021–T023** add vegetarian filtering for User Story 3.
