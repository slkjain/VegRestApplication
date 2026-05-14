import os
from typing import Dict, List, Optional

import openai
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GOOGLE_PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

OPENAI_MODEL = "gpt-5"

def get_google_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise EnvironmentError("GOOGLE_API_KEY environment variable is required.")
    return key


def get_openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is required.")
    return key


def search_restaurants(location: str) -> List[Dict]:
    params = {
        "query": f"restaurants near {location}",
        "type": "restaurant",
        "key": get_google_api_key(),
    }
    response = requests.get(GOOGLE_PLACES_SEARCH_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "OK":
        error_msg = payload.get('error_message', '')
        if "REQUEST_DENIED" in payload.get("status", ""):
            error_msg = (
                "REQUEST_DENIED: The Places API is not enabled for your Google Cloud project. "
                "Enable it at https://console.cloud.google.com/apis/library/places-backend.googleapis.com"
            )
        raise RuntimeError(f"Google Places search error: {payload.get('status')} - {error_msg}")

    return payload.get("results", [])


def fetch_restaurant_reviews(place_id: str) -> List[Dict]:
    params = {
        "place_id": place_id,
        "fields": "review",
        "key": get_google_api_key(),
    }
    response = requests.get(GOOGLE_PLACE_DETAILS_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "OK":
        error_msg = payload.get('error_message', '')
        if "REQUEST_DENIED" in payload.get("status", ""):
            error_msg = (
                "REQUEST_DENIED: The Places API is not enabled for your Google Cloud project. "
                "Enable it at https://console.cloud.google.com/apis/library/places-backend.googleapis.com"
            )
        raise RuntimeError(f"Google Place details error: {payload.get('status')} - {error_msg}")

    result = payload.get("result", {})
    return result.get("reviews", [])


def _build_classification_prompt(name: str, address: str, reviews: List[Dict]) -> str:
    review_texts = []
    for review in reviews[:3]:
        text = review.get("text") or review.get("review") or ""
        if text:
            review_texts.append(f"- {text}")

    review_block = "\n".join(review_texts) if review_texts else "No review text available."

    prompt = (
        "You are a food classification assistant. Determine whether the following restaurant is a pure vegetarian restaurant. "
        "Pure vegetarian means the restaurant does not serve meat, fish, or animal products. "
        "Respond with exactly one of: Pure Vegetarian, Not Pure Vegetarian, Unknown.\n\n"
        f"Restaurant: {name}\n"
        f"Address: {address}\n"
        "Reviews:\n"
        f"{review_block}\n\n"
        "Based on the available information, is this restaurant pure vegetarian?"
    )
    return prompt


def classify_restaurant(name: str, address: str, reviews: List[Dict]) -> str:
    openai.api_key = get_openai_api_key()
    prompt = _build_classification_prompt(name, address, reviews)

    response = openai.responses.create(
        model=OPENAI_MODEL,
        reasoning={"effort": "low"},
        input=[
            {"role": "system", "content": "Classify restaurants as Pure Vegetarian, Not Pure Vegetarian, or Unknown based on reviews."},
            {"role": "user", "content": prompt},
        ],
        max_output_tokens=50,
        # temperature=0.0, #this is not a supported parameter for gpt-5
    )

    if hasattr(response, "output_text") and response.output_text:
        content = response.output_text.strip()
    else:
        content = ""
        if getattr(response, "output", None):
            output_blocks = response.output
            if output_blocks and getattr(output_blocks[0], "content", None):
                first_content = output_blocks[0].content
                if first_content and getattr(first_content[0], "text", None):
                    content = first_content[0].text.strip()

    normalized = content.split("\n")[0].strip() if content else "Unknown"

    if normalized not in {"Pure Vegetarian", "Not Pure Vegetarian", "Unknown"}:
        normalized_text = normalized.lower()
        if "pure vegetarian" in normalized_text:
            return "Pure Vegetarian"
        if "not pure" in normalized_text or "not vegetarian" in normalized_text:
            return "Not Pure Vegetarian"
        return "Unknown"
    return normalized


def extract_review_snippet(reviews: List[Dict]) -> Optional[str]:
    for review in reviews:
        text = review.get("text") or review.get("review")
        if text:
            return text[:250]
    return None
