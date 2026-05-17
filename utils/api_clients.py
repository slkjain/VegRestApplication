import json
import os
import re
from typing import Any, Dict, List, Optional

import openai
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GOOGLE_PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
GOOGLE_PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

OPENAI_MODEL = "gpt-5"

SYSTEM_PROMPT = """You are a dietary analysis assistant. You will be given a details of a restaurant including a collection
of the restaurant reviews. Your job is to determine whether the restaurant is suitable
for each of the following diets based solely on what is mentioned in the restaurant details:

- Vegan: only plant based products, no animal products at all (no meat, no fish, no dairy, no eggs, no honey, etc.)
- LactoVegetarian: no meat or eggs, but milk and honey are allowed. (no meat, no fish, no eggs, no chicken, etc.)

*Very Important*: Remember that if non-vegetarian dishes or eggs are served then 
that restaurant is not suitable for Vegan or LactoVegetarian.

Return ONLY a valid JSON object with exactly these keys.    
Do not include any explanation, markdown, or extra text — only the JSON.

Example output:
{
  "Vegan": true,# set this to false if non-vegetarian dishes are also served
  "LactoVegetarian": true,# set this to false if non-vegetarian dishes are also served
  "Justification": "The reviews indicate that both vegan and vegetarian dishes are served while non-veg dishes are not served."
}

If the restaurant details do not contain enough information to confirm a diet is supported,
default that value to false.
"""

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
    # for review in reviews[:3]:
    for review in reviews:
        text = review.get("text") or review.get("review") or ""
        if text:
            review_texts.append(f"- {text}")

    review_block = "\n".join(review_texts) if review_texts else "No review text available."

    # prompt = (
    #     "You are a food classification assistant. Determine whether the following restaurant is a pure vegetarian restaurant. "
    #     "Pure vegetarian means the restaurant does not serve meat, fish, or animal products. "
    #     "Respond with exactly one of: Pure Vegetarian, Not Pure Vegetarian, Unknown.\n\n"
    #     f"Restaurant: {name}\n"
    #     f"Address: {address}\n"
    #     "Reviews:\n"
    #     f"{review_block}\n\n"
    #     "Based on the available information, is this restaurant pure vegetarian?"
    # )

    prompt = f"Restaurant reviews:\n\n{review_block}"
    return prompt


def classify_restaurant(name: str, address: str, reviews: List[Dict]) -> Dict[str, Any]:
    openai.api_key = get_openai_api_key()
    prompt = _build_classification_prompt(name, address, reviews)

    response = openai.responses.create(
        model=OPENAI_MODEL,
        reasoning={"effort": "low"},
        input=[
            #{"role": "system", "content": "Classify restaurants as Pure Vegetarian, Not Pure Vegetarian, or Unknown based on reviews."},
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        max_output_tokens=None, #50
        # temperature=0.0, #this is not a supported parameter for gpt-5
    )

    raw = ""
    if getattr(response, "output_text", None):
        raw = response.output_text.strip()
    elif getattr(response, "output", None):
        for output_entry in response.output:
            for content_item in getattr(output_entry, "content", []) or []:
                content_text = getattr(content_item, "text", None)
                if content_text:
                    raw += content_text
            if raw:
                break
    elif getattr(response, "choices", None):
        raw = response.choices[0].message.content.strip()

    if not raw:
        raise ValueError("OpenAI response did not contain any text output.")

    # Strip markdown fences if the model adds them despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    # Remove inline comments from the JSON string so values like
    # "true,# ..." can still be parsed safely.
    raw = re.sub(r'(?m)\s*(?:#|//).*$', '', raw).strip()

    result = json.loads(raw)

    # Validate expected keys are present
    expected_keys = {"Vegan", "LactoVegetarian", "Justification"}
    missing = expected_keys - result.keys()
    if missing:
        raise ValueError(f"Model response missing expected keys: {missing}")

    return {k: result[k] for k in expected_keys}

def extract_review_snippet(reviews: List[Dict]) -> Optional[str]:
    for review in reviews:
        text = review.get("text") or review.get("review")
        if text:
            return text[:250]
    return None
