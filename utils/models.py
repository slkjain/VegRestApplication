import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


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
    is_pure_vegetarian: Optional[bool]
    is_vegan: Optional[bool]
    review_snippet: Optional[str]
    reviews: List[Review]
    restaurant_image_url: Optional[str] = None
    justification: Optional[str] = None


def build_restaurant(
    result: dict,
    classification: Union[str, Dict[str, Any]],
    review_snippet: Optional[str],
    reviews: List[Review],
    restaurant_image_url: Optional[str] = None,
) -> Restaurant:
    classification_data: Dict[str, Any] = {}
    if isinstance(classification, str):
        sanitized_classification = re.sub(r'(?m)\s*(?:#|//).*$', '', classification)
        try:
            classification_data = json.loads(sanitized_classification)
        except json.JSONDecodeError:
            classification_data = {}
    elif isinstance(classification, dict):
        classification_data = classification

    vegan_value = classification_data.get("Vegan")
    lacto_value = classification_data.get("LactoVegetarian")

    def _normalize_bool(value: Any) -> Optional[bool]:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "1"}:
                return True
            if lowered in {"false", "no", "0"}:
                return False
        return None

    is_vegan = _normalize_bool(vegan_value)
    is_lacto = _normalize_bool(lacto_value)
    is_pure_vegetarian = None
    if is_vegan is not None or is_lacto is not None:
        is_pure_vegetarian = bool(is_vegan or is_lacto)

    justification = classification_data.get("Justification")

    return Restaurant(
        id=result.get("place_id", ""),
        name=result.get("name", "Unknown"),
        address=result.get("formatted_address", "Unknown address"),
        rating=result.get("rating"),
        is_pure_vegetarian=is_pure_vegetarian,
        is_vegan=is_vegan,
        review_snippet=review_snippet,
        reviews=reviews,
        restaurant_image_url=restaurant_image_url,
        justification=justification,
    )
