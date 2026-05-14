from utils.api_clients import extract_review_snippet


def test_extract_review_snippet_returns_first_available_text():
    reviews = [
        {"author_name": "A", "text": "Delicious food"},
        {"author_name": "B", "text": "Good service"},
    ]

    snippet = extract_review_snippet(reviews)

    assert snippet == "Delicious food"


def test_extract_review_snippet_returns_none_when_no_text():
    reviews = [{"author_name": "A"}, {"author_name": "B", "review": ""}]

    snippet = extract_review_snippet(reviews)

    assert snippet is None
