from utils.api_clients import extract_review_snippet, search_restaurants


def test_extract_review_snippet_returns_first_available_text():
    reviews = [
        {"author_name": "A", "text": "Delicious food"},
        {"author_name": "B", "text": "Good service"},
    ]

    snippet = extract_review_snippet(reviews)

    assert snippet == "Delicious food"


def test_search_restaurants_returns_top_results(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "OK",
                "results": [
                    {"name": "A", "place_id": "1"},
                    {"name": "B", "place_id": "2"},
                    {"name": "C", "place_id": "3"},
                    {"name": "D", "place_id": "4"},
                    {"name": "E", "place_id": "5"},
                    {"name": "F", "place_id": "6"},
                ],
            }

    def dummy_get(url, params=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr("utils.api_clients.requests.get", dummy_get)

    results = search_restaurants("vegan", "Austin")

    assert len(results) == 5
    assert results[0]["name"] == "A"
    assert results[-1]["name"] == "E"


def test_search_restaurants_raises_when_no_results(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "OK", "results": []}

    def dummy_get(url, params=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr("utils.api_clients.requests.get", dummy_get)

    try:
        search_restaurants("vegan", "Austin")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No restaurants found" in str(exc)


def test_extract_review_snippet_returns_none_when_no_text():
    reviews = [{"author_name": "A"}, {"author_name": "B", "review": ""}]

    snippet = extract_review_snippet(reviews)

    assert snippet is None
