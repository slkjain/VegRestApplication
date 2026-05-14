from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Review:
    author_name: Optional[str]
    rating: Optional[int]
    relative_time_description: Optional[str]
    text: str


@dataclass
class Restaurant:
    id: str
    name: str
    address: str
    rating: Optional[float]
    is_pure_vegetarian: Optional[str]
    review_snippet: Optional[str]
    reviews: List[Review]


def build_restaurant(result: dict, classification: str, review_snippet: Optional[str], reviews: List[Review]) -> Restaurant:
    return Restaurant(
        id=result.get("place_id", ""),
        name=result.get("name", "Unknown"),
        address=result.get("formatted_address", "Unknown address"),
        rating=result.get("rating"),
        is_pure_vegetarian=classification,
        review_snippet=review_snippet,
        reviews=reviews,
    )
