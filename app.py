import os
from typing import List, Optional

import streamlit as st

from utils.api_clients import (
    MAX_SEARCH_RESULTS,
    build_photo_url,
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
        body {
            background: linear-gradient(180deg, #f8fbff 0%, #ffffff 50%, #f3f8f9 100%);
            color: #0f172a;
        }
        .hero {
            padding: 48px 32px 32px;
            border-radius: 24px;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 18px 50px rgba(34, 76, 127, 0.08);
            margin-bottom: 32px;
        }
        .hero h1 {
            margin: 0 0 12px;
            font-size: 3rem;
            line-height: 1.05;
            letter-spacing: -0.04em;
        }
        .hero p {
            margin: 0;
            font-size: 1.05rem;
            color: #475569;
            line-height: 1.7;
        }
        .search-card {
            background: #ffffff;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
            margin-bottom: 32px;
        }
        .results-note {
            margin-top: 0.35rem;
            color: #475569;
            font-size: 0.98rem;
        }
        .restaurant-grid {
            display: grid;
            gap: 20px;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
        }
        .restaurant-card {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 20px;
            padding: 22px;
            background: #ffffff;
            box-shadow: 0 10px 32px rgba(15, 23, 42, 0.05);
        }
        .restaurant-card h3 {
            margin-top: 0;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 700;
            margin-right: 8px;
            margin-bottom: 8px;
        }
        .status-pure { background: #def7ec; color: #046c4e; }
        .status-vegan { background: #dbeafe; color: #1e40af; }
        .status-not { background: #fee2e2; color: #991b1b; }
        .status-unknown { background: #fef3c7; color: #92400e; }
        .review-snippet {
            margin-top: 12px;
            color: #334155;
            font-size: 0.95rem;
        }
        .restaurant-meta {
            color: #475569;
            font-size: 0.95rem;
            margin-bottom: 8px;
        }
        .restaurant-card img {
            width: 100%;
            border-radius: 16px;
            margin-top: 16px;
        }
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
    if "restaurant_name" not in st.session_state:
        st.session_state.restaurant_name = ""
    if "location" not in st.session_state:
        st.session_state.location = ""
    if "error_message" not in st.session_state:
        st.session_state.error_message = ""


def map_status_classification(is_pure_vegetarian: Optional[bool]) -> str:
    if is_pure_vegetarian is True:
        return "status-pure"
    if is_pure_vegetarian is False:
        return "status-not"
    return "status-unknown"


def render_restaurant_card(restaurant: Restaurant) -> None:
    pure_class = map_status_classification(restaurant.is_pure_vegetarian)
    pure_text = (
        "Pure Vegetarian"
        if restaurant.is_pure_vegetarian is True
        else "Not Pure Vegetarian"
        if restaurant.is_pure_vegetarian is False
        else "Unknown"
    )
    vegan_class = (
        "status-vegan"
        if restaurant.is_vegan is True
        else "status-not"
        if restaurant.is_vegan is False
        else "status-unknown"
    )
    vegan_text = (
        "Vegan"
        if restaurant.is_vegan is True
        else "Not Vegan"
        if restaurant.is_vegan is False
        else "Unknown"
    )
    st.markdown("<div class='restaurant-card'>", unsafe_allow_html=True)
    st.markdown(f"### {restaurant.name}")
    st.markdown(f"**Address:** {restaurant.address}")
    if restaurant.rating is not None:
        st.markdown(f"**Rating:** {restaurant.rating}")
    st.markdown(
        f"<span class='status-pill {pure_class}'>{pure_text}</span>"
        f"<span class='status-pill {vegan_class}'>{vegan_text}</span>",
        unsafe_allow_html=True,
    )
    if restaurant.justification:
        st.markdown(f"**Justification:** {restaurant.justification}")
    if restaurant.review_snippet:
        st.markdown(f"<div class='review-snippet'>{restaurant.review_snippet}</div>", unsafe_allow_html=True)
    with st.expander("View reviews"):
        if restaurant.reviews:
            for review in restaurant.reviews:
                st.markdown(f"**{review.author_name or 'Reviewer'}** · {review.rating or '-'} stars · {review.relative_time_description or ''}")
                st.markdown(f"> {review.text}")
                st.markdown("---")
        else:
            st.info("No reviews are available for this restaurant.")
    if restaurant.restaurant_image_url:
        st.markdown("**Restaurant Image:**")
        st.image(restaurant.restaurant_image_url, caption="Restaurant", width=700)
    st.markdown("</div>", unsafe_allow_html=True)


def classify_search_results(results: List[dict]) -> List[Restaurant]:
    restaurants: List[Restaurant] = []
    for result in results:
        try:
            details = fetch_restaurant_reviews(result.get("place_id", ""))
            review_list = details.get("reviews", [])
            classification = classify_restaurant(
                result.get("name", "Unknown"),
                result.get("formatted_address", ""),
                review_list,
            )
            snippet = extract_review_snippet(review_list)
            reviews = []
            for review in review_list[:5]:
                reviews.append(
                    Review(
                        author_name=review.get("author_name"),
                        rating=review.get("rating"),
                        relative_time_description=review.get("relative_time_description"),
                        text=review.get("text", ""),
                    )
                )
            restaurant_image_url = None
            photos = details.get("photos", [])
            if photos:
                photo_reference = photos[0].get("photo_reference")
                if photo_reference:
                    restaurant_image_url = build_photo_url(photo_reference)
            restaurant = build_restaurant(result, classification, snippet, reviews, restaurant_image_url)
            restaurants.append(restaurant)
        except Exception as exc:
            st.warning(f"Failed to classify {result.get('name', 'restaurant')}: {exc}")
    return restaurants


def on_search() -> None:
    restaurant_name = st.session_state.restaurant_name.strip()
    location = st.session_state.location.strip()
    st.session_state.error_message = ""
    if not restaurant_name or not location:
        st.session_state.error_message = "Please enter both restaurant name and location to search."
        st.session_state.restaurants = []
        return

    try:
        with st.spinner("Searching restaurants and analyzing vegetarian/vegan status..."):
            raw_results = search_restaurants(restaurant_name, location)
            st.session_state.restaurants = classify_search_results(raw_results)
    except Exception as exc:
        st.session_state.restaurants = []
        st.session_state.error_message = str(exc)


def main() -> None:
    st.set_page_config(page_title="Veg Restaurant Checker", layout="wide")
    create_session_state()
    local_css()

    st.markdown(
        """
        <div class="hero">
            <h1>Veg Restaurant Checker</h1>
            <p>Search multiple restaurants at once and see vegetarian and vegan suitability in a polished, modern interface.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    env_message = get_env_message()
    if env_message:
        st.error(env_message)
        return

    st.markdown("<div class='search-card'>", unsafe_allow_html=True)
    with st.form(key="search_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.session_state.restaurant_name = st.text_input("Restaurant name or keyword", value=st.session_state.restaurant_name)
        with col2:
            st.session_state.location = st.text_input("Location", value=st.session_state.location)
        submitted = st.form_submit_button("Search")
        if submitted:
            on_search()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    if st.session_state.restaurants:
        st.markdown(f"#### Results ({len(st.session_state.restaurants)})")
        st.markdown(f"<p class='results-note'>Showing up to {MAX_SEARCH_RESULTS} matching restaurants for your query.</p>", unsafe_allow_html=True)
        with st.container():
            cols = st.columns(2)
            for index, restaurant in enumerate(st.session_state.restaurants):
                with cols[index % 2]:
                    render_restaurant_card(restaurant)
    elif not st.session_state.error_message:
        st.info("Enter a restaurant name and location and press Search.")

if __name__ == "__main__":
    main()
