import os
from typing import List, Optional

import streamlit as st

from utils.api_clients import (
    classify_restaurant,
    extract_review_snippet,
    fetch_restaurant_reviews,
    search_restaurants,
)
from utils.models import Restaurant, Review, build_restaurant


def local_css() -> None:
    st.markdown(
        """
        <style>
        .restaurant-card {
            border: 1px solid #e6e6e6;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            background: #fff;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
        }
        .status-pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        .status-pure { background: #d4f5d4; color: #1f6b1f; }
        .status-not { background: #ffe2e0; color: #8b1a1a; }
        .status-unknown { background: #f7f0d6; color: #705b10; }
        .review-snippet { margin-top: 8px; color: #555; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_env_message() -> Optional[str]:
    missing = []
    if not os.getenv("GOOGLE_API_KEY"):
        missing.append("GOOGLE_API_KEY")
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if missing:
        return f"Missing environment variables: {', '.join(missing)}. Set them before running the app."
    return None


def create_session_state() -> None:
    if "restaurants" not in st.session_state:
        st.session_state.restaurants = []
    if "location" not in st.session_state:
        st.session_state.location = ""
    if "filter_vegetarian" not in st.session_state:
        st.session_state.filter_vegetarian = False
    if "error_message" not in st.session_state:
        st.session_state.error_message = ""


def map_status_classification(status: str) -> str:
    if status == "Pure Vegetarian":
        return "status-pure"
    if status == "Not Pure Vegetarian":
        return "status-not"
    return "status-unknown"


def render_restaurant_card(restaurant: Restaurant) -> None:
    status_class = map_status_classification(restaurant.is_pure_vegetarian or "Unknown")
    st.markdown("<div class='restaurant-card'>", unsafe_allow_html=True)
    st.markdown(f"### {restaurant.name}")
    st.markdown(f"**Address:** {restaurant.address}")
    if restaurant.rating is not None:
        st.markdown(f"**Rating:** {restaurant.rating}")
    st.markdown(
        f"<span class='status-pill {status_class}'>{restaurant.is_pure_vegetarian or 'Unknown'}</span>",
        unsafe_allow_html=True,
    )
    if restaurant.review_snippet:
        st.markdown(f"<div class='review-snippet'>{restaurant.review_snippet}...</div>", unsafe_allow_html=True)
    with st.expander("View reviews"):
        if restaurant.reviews:
            for review in restaurant.reviews:
                st.markdown(f"**{review.author_name or 'Reviewer'}** · {review.rating or '-'} stars · {review.relative_time_description or ''}")
                st.markdown(f"> {review.text}")
                st.markdown("---")
        else:
            st.info("No reviews are available for this restaurant.")
    st.markdown("</div>", unsafe_allow_html=True)


def classify_search_results(results: List[dict]) -> List[Restaurant]:
    restaurants: List[Restaurant] = []
    for result in results:
        try:
            reviews_data = fetch_restaurant_reviews(result.get("place_id", ""))
            classification = classify_restaurant(
                result.get("name", "Unknown"),
                result.get("formatted_address", ""),
                reviews_data,
            )
            snippet = extract_review_snippet(reviews_data)
            reviews = []
            for review in reviews_data[:5]:
                reviews.append(
                    Review(
                        author_name=review.get("author_name"),
                        rating=review.get("rating"),
                        relative_time_description=review.get("relative_time_description"),
                        text=review.get("text", ""),
                    )
                )
            restaurant = build_restaurant(result, classification, snippet, reviews)
            restaurants.append(restaurant)
        except Exception as exc:
            st.warning(f"Failed to classify {result.get('name', 'restaurant')}: {exc}")
    return restaurants


def on_search() -> None:
    location = st.session_state.location.strip()
    st.session_state.error_message = ""
    if not location:
        st.session_state.error_message = "Please enter a location or address to search."
        st.session_state.restaurants = []
        return

    try:
        with st.spinner("Searching restaurants and analyzing vegetarian status..."):
            raw_results = search_restaurants(location)
            st.session_state.restaurants = classify_search_results(raw_results[:5])
    except Exception as exc:
        st.session_state.restaurants = []
        st.session_state.error_message = str(exc)


def filter_restaurants(restaurants: List[Restaurant], only_vegetarian: bool) -> List[Restaurant]:
    if not only_vegetarian:
        return restaurants
    return [r for r in restaurants if r.is_pure_vegetarian == "Pure Vegetarian"]


def main() -> None:
    st.set_page_config(page_title="Veg Restaurant Finder", layout="wide")
    create_session_state()
    local_css()

    st.title("Veg Restaurant Finder")
    st.write("Search restaurants by location and check whether they are pure vegetarian using Google and OpenAI APIs.")

    env_message = get_env_message()
    if env_message:
        st.error(env_message)
        return

    with st.form(key="search_form"):
        st.session_state.location = st.text_input("Location", value=st.session_state.location)
        st.session_state.filter_vegetarian = st.checkbox("Show only pure vegetarian restaurants", value=st.session_state.filter_vegetarian)
        submitted = st.form_submit_button("Search")
        if submitted:
            on_search()

    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    if st.session_state.restaurants:
        filtered = filter_restaurants(st.session_state.restaurants, st.session_state.filter_vegetarian)
        if not filtered:
            st.info("No restaurants match the selected filter. Try a broader search or disable the vegetarian-only filter.")
        else:
            st.markdown(f"#### Results ({len(filtered)})")
            for restaurant in filtered:
                render_restaurant_card(restaurant)
    elif not st.session_state.error_message:
        st.info("Enter a location and press Search to discover restaurants.")


if __name__ == "__main__":
    main()
